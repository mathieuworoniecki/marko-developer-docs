#!/usr/bin/env python3
"""Read runtime-matching backend models without starting the API or connecting to a DB.

Run with the backend's existing Python environment. Output is temporary; only the
publicly reachable schemas are included by build-reference.py.
"""
import argparse
import ast
import inspect
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import textwrap

parser = argparse.ArgumentParser()
parser.add_argument("--backend", type=Path, required=True)
parser.add_argument("--sha", required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--examples", type=Path, help="Validate final synthetic JSON request examples with the actual Pydantic body fields")
args = parser.parse_args()
head = subprocess.check_output(["git", "-C", str(args.backend), "rev-parse", "HEAD"], text=True).strip()
if head != args.sha:
    raise SystemExit("Backend HEAD differs from the verified served SHA")
for staged in (False, True):
    command = ["git", "-C", str(args.backend), "diff", "--quiet"]
    if staged:
        command.append("--cached")
    if subprocess.run(command).returncode:
        raise SystemExit("Backend contains tracked changes; use a clean matching checkout")
os.environ["MARKO_E2E_IGNORE_ROOT_ENV"] = "1"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://docs:docs@127.0.0.1:1/docs"
sys.dont_write_bytecode = True
sys.path.insert(0, str(args.backend.resolve()))

def no_network(*_args, **_kwargs):
    raise RuntimeError("Network disabled during documentation schema extraction")

socket.socket.connect = no_network
socket.create_connection = no_network

from fastapi import FastAPI
from app.routers import comments, operations, reporting_templates
from app.routers.public_api import public_v1
from app.services import privacy_export_service as privacy
from app.services.workflow_execution_service import list_workflow_presets
from app.models.privacy_case import PrivacyCaseStatus
from app.schemas import saved_view
from starlette import status

def declared_error_statuses(function, depth=0, seen=None):
    """Only literal HTTPException statuses in handlers and named app helpers."""
    seen = set() if seen is None else seen
    if function in seen or depth > 3 or not inspect.isfunction(function):
        return set()
    if not function.__module__.startswith("app."):
        return set()
    seen.add(function)
    try:
        tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
    except (OSError, TypeError):
        return set()
    codes = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
        if name == "HTTPException":
            expression = next((value.value for value in node.keywords if value.arg == "status_code"), node.args[0] if node.args else None)
            if isinstance(expression, ast.Constant) and isinstance(expression.value, int):
                codes.add(expression.value)
            elif isinstance(expression, ast.Attribute) and expression.attr.startswith("HTTP_"):
                code = getattr(status, expression.attr, None)
                if isinstance(code, int):
                    codes.add(code)
        called = None
        if isinstance(node.func, ast.Name):
            called = function.__globals__.get(node.func.id)
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            module = function.__globals__.get(node.func.value.id)
            if inspect.ismodule(module) and module.__name__.startswith("app."):
                called = getattr(module, node.func.attr, None)
        if inspect.isfunction(called):
            codes.update(declared_error_statuses(called, depth + 1, seen))
        for keyword in node.keywords:
            if keyword.arg == "handler" and isinstance(keyword.value, ast.Attribute) and isinstance(keyword.value.value, ast.Name):
                module = function.__globals__.get(keyword.value.value.id)
                if inspect.ismodule(module):
                    handler = getattr(module, keyword.value.attr, None)
                    if inspect.isfunction(handler):
                        codes.update(declared_error_statuses(handler, depth + 1, seen))
    return {code for code in codes if 400 <= code < 600}

app = FastAPI()
app.include_router(public_v1)
extra = {}
for name, router, endpoint in [
    ("comments_list", comments.router, comments.list_comments),
    ("comment", comments.router, comments.create_comment),
    ("chronicle", operations.router, operations.get_operation_chronicle),
    ("chronicle_narrative", operations.router, operations.get_operation_chronicle_narrative),
]:
    model = next(route.response_model for route in router.routes if route.endpoint is endpoint)
    path = f"/__documentation/{name}"
    app.add_api_route(path, lambda: None, response_model=model)
    extra[name] = path
spec = app.openapi()
spec["x-documentation-extra-models"] = {
    name: spec["paths"][path]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    for name, path in extra.items()
}
spec["x-documentation-source-sha"] = head
spec["x-documentation-error-statuses"] = {
    f"{method.lower()} {route.path}": sorted(declared_error_statuses(route.endpoint))
    for route in public_v1.routes for method in route.methods
}
spec["x-documentation-presets"] = list_workflow_presets()
spec["x-documentation-privacy-statuses"] = [status.value for status in PrivacyCaseStatus]
spec["x-documentation-saved-view-constraints"] = {
    "icons": sorted(saved_view.SAVED_VIEW_ICON_TOKENS),
    "colors": sorted(saved_view.SAVED_VIEW_COLOR_TOKENS),
    "operation_filters": sorted(saved_view._OPERATIONS_FILTER_KEYS),
    "operation_columns": sorted(saved_view._OPERATIONS_COLUMN_KEYS),
    "operation_sort": sorted(saved_view._OPERATIONS_SORT_KEYS),
}

# RGPD serializers expose a projection, never every underlying model column.
# Extract that projection's exact keys. SQLAlchemy types describe direct column
# values; JSON columns intentionally retain an open JSON shape.
JSON_VALUE = {"description": "Valeur JSON métier dont la structure dépend de la source."}

def obj(properties):
    return {"type": "object", "properties": properties, "required": list(properties)}

def nullable(schema):
    return {"anyOf": [schema, {"type": "null"}]}

def column_schema(model, key):
    try:
        column = getattr(model, key).property.columns[0]
        kind = column.type.python_type
    except (AttributeError, KeyError, NotImplementedError):
        return dict(JSON_VALUE)
    import datetime
    import decimal
    import enum
    import uuid
    if isinstance(kind, type) and issubclass(kind, enum.Enum):
        schema = {"type": "string", "enum": [value.value for value in kind]}
    elif kind is bool:
        schema = {"type": "boolean"}
    elif kind is int:
        schema = {"type": "integer"}
    elif kind is decimal.Decimal:
        schema = {"type": "string", "description": "Valeur décimale sérialisée en chaîne dans cet export JSON."}
    elif kind is float:
        schema = {"type": "number"}
    elif kind is uuid.UUID:
        schema = {"type": "string", "format": "uuid"}
    elif kind in (datetime.datetime, datetime.date):
        schema = {"type": "string", "format": "date-time" if kind is datetime.datetime else "date"}
    elif kind is str:
        schema = {"type": "string"}
    else:
        return dict(JSON_VALUE)
    return nullable(schema) if column.nullable else schema

def serializer_schema(serializer, model):
    source = ast.parse(textwrap.dedent(inspect.getsource(serializer)))
    # A few source specs use a lambda solely to supply current-user arguments.
    lambdas = [node for node in ast.walk(source) if isinstance(node, ast.Lambda)]
    if lambdas:
        called = lambdas[0].body
        if isinstance(called, ast.Call):
            name = called.func.attr if isinstance(called.func, ast.Attribute) else called.func.id
            function = getattr(privacy.PrivacyExportService, name, getattr(privacy, name, None))
            if function:
                return serializer_schema(function, model)
    assignments = {}
    for node in ast.walk(source):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments[target.id] = node.value

    field_tuple = assignments.get("fields")
    if isinstance(field_tuple, (ast.Tuple, ast.List)):
        fields = [node.value for node in field_tuple.elts if isinstance(node, ast.Constant)]
        return obj({key: column_schema(model, key) for key in fields})
    for node in ast.walk(source):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_serialize":
            fields = ast.literal_eval(node.args[1])
            return obj({key: column_schema(model, key) for key in fields})

    def expression(node):
        if isinstance(node, ast.Name) and node.id in assignments:
            return expression(assignments[node.id])
        if isinstance(node, ast.Constant):
            if node.value is None:
                return {"type": "null"}
            if isinstance(node.value, bool):
                return {"type": "boolean"}
            if isinstance(node.value, int):
                return {"type": "integer"}
            if isinstance(node.value, float):
                return {"type": "number"}
            return {"type": "string"}
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "row":
            return column_schema(model, node.attr)
        if isinstance(node, ast.Dict):
            return obj({key.value: expression(value) for key, value in zip(node.keys, node.values) if isinstance(key, ast.Constant)})
        if isinstance(node, ast.IfExp):
            left, right = expression(node.body), expression(node.orelse)
            return left if left == right else {"anyOf": [left, right]}
        if isinstance(node, ast.List):
            return {"type": "array", "items": expression(node.elts[0]) if node.elts else dict(JSON_VALUE)}
        if isinstance(node, (ast.ListComp, ast.GeneratorExp)):
            return {"type": "array", "items": expression(node.elt)}
        if isinstance(node, ast.Call):
            name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
            if name in ("_iso", "isoformat", "_isoformat"):
                return nullable({"type": "string", "format": "date-time"})
            if name == "_enum" and node.args:
                return expression(node.args[0])
            if name in ("str", "bool", "int", "float"):
                return {"type": {"str": "string", "bool": "boolean", "int": "integer", "float": "number"}[name]}
            if name == "dict":
                return {"type": "object", "additionalProperties": True, **JSON_VALUE}
            if name == "list":
                return {"type": "array", "items": dict(JSON_VALUE)}
        if isinstance(node, (ast.Compare, ast.BoolOp)):
            return {"type": "boolean"}
        return dict(JSON_VALUE)

    returns = [node.value for node in ast.walk(source) if isinstance(node, ast.Return)]
    if not returns:
        raise ValueError(f"No serializer return: {serializer}")
    return expression(returns[-1])

service = object.__new__(privacy.PrivacyExportService)
service.user_id = "documentation-subject"
service.entity_slug = "documentation-entity"
service.data_environment = "live"
table_schemas = {}
for source in service._entity_array_sources():
    # Registered sources build their fields from the reviewed registry. The
    # serializer's bound lambda holds its registry spec in its defaults.
    defaults = getattr(source.serializer, "__defaults__", ()) or ()
    registered = next((value for value in defaults if isinstance(value, privacy.PrivacyPersonalSource)), None)
    if registered:
        properties = {
            "source_id": {"type": "string"}, "registry_version": {"type": "string"},
            "relationship_fields": {"type": "array", "items": {"type": "string"}},
            "embedded_subject_reference": {"type": "boolean"}, "derived_relationship": {"type": "boolean"},
        }
        properties.update({key: column_schema(source.model, key) for key in registered.export_fields})
        schema = obj(properties)
    else:
        schema = serializer_schema(source.serializer, source.model)
    if not schema.get("properties"):
        raise ValueError(f"Serializer projection unresolved: {source.key}")
    schema["description"] = f"Projection exportée pour {source.key}; couverture: {source.coverage}. Champs exclus: {', '.join(source.excluded_fields) or 'aucun champ supplémentaire déclaré'}."
    table_schemas[source.key] = {"type": "array", "items": schema}
spec["x-documentation-privacy-tables"] = table_schemas
spec["x-documentation-privacy-profile"] = serializer_schema(privacy.PrivacyExportService._serialize_user, privacy.User)
spec["x-documentation-privacy-central"] = {
    "demo_state": {"type": "array", "items": serializer_schema(privacy.PrivacyExportService._serialize_demo_state, privacy.DemoUserState)},
    "privacy_cases": {"type": "array", "items": serializer_schema(privacy.PrivacyExportService._serialize_privacy_case, privacy.PrivacyCase)},
    "pappers_request_metadata": {"type": "array", "items": serializer_schema(privacy.PrivacyExportService._serialize_pappers_request, privacy.PappersRequestReservation)},
}
args.output.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n")
print(f"Extracted {len(spec['components']['schemas'])} native models and {len(table_schemas)} RGPD projections from {head}")
if args.examples:
    documented = json.loads(args.examples.read_text())
    failures = []
    checked = 0
    for route in public_v1.routes:
        for method in route.methods:
            operation = documented.get("paths", {}).get(route.path, {}).get(method.lower())
            if not operation or not route.body_field:
                continue
            media = operation.get("requestBody", {}).get("content", {}).get("application/json", {})
            if "example" not in media:
                continue
            _value, errors = route.body_field.validate(media["example"], {}, loc=("body",))
            checked += 1
            if errors:
                failures.append(f"{method} {route.path}: {errors}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"PASS: {checked} synthetic JSON request examples validated by actual runtime-matching Pydantic models, without invoking handlers")
