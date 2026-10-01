#!/usr/bin/env python3
"""Verify the published contract, examples, documentation and optional live drift."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import urllib.request
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
METHODS = {"get", "post", "put", "patch", "delete"}

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def build_download(document):
    config = json.loads((ROOT / "docs.json").read_text())
    pages = [page for group in config["navigation"]["groups"] for page in group.get("pages", [])]
    sections = ["# MARKO — Documentation complète\n\nGuides et référence des opérations publiques stables. Exemples synthétiques.\n"]
    for page in pages:
        content = (ROOT / f"{page}.mdx").read_text()
        parts = content.split("---", 2)
        metadata, body = parts[1], parts[2]
        title = re.search(r'^title:\s*"(.+)"', metadata, re.M).group(1)
        body = re.sub(r'^import .+$', '', body, flags=re.M)
        body = re.sub(r'<CopyDocumentation\s*/>', '', body)
        sections.append(f"\n# {title}\n\nSource: https://developers.marko.fr/{page}\n{body.strip()}\n")
    sections.append("\n# Contrat OpenAPI complet\n\nLes $ref ci-dessous sont résolus dans components.schemas du même document.\n\n```json\n" + json.dumps(document, ensure_ascii=False, indent=2) + "\n```\n")
    return "\n".join(sections)

def check(document):
    errors, operations = [], []
    examples = 0
    checker = FormatChecker()
    components = document["components"]["schemas"]
    def resolve(schema):
        if "$ref" in schema:
            return resolve(components[schema["$ref"].rsplit("/", 1)[-1]])
        return schema
    def check_example(schema, value, label):
        nonlocal examples
        examples += 1
        validator = Draft202012Validator({"components": document["components"], **schema}, format_checker=checker)
        for error in validator.iter_errors(value):
            errors.append(f"{label}: {list(error.path)} {error.message}")
    for schema in components.values():
        Draft202012Validator.check_schema(schema)
    for path, item in document["paths"].items():
        for method, operation in item.items():
            if method not in METHODS:
                continue
            label = f"{method.upper()} {path}"
            operations.append(operation["operationId"])
            if operation.get("x-marko-stability") != "ga":
                errors.append(f"{label}: non-GA operation")
            scope = operation.get("x-marko-required-scope")
            if scope and f"`{scope}`" not in operation["description"]:
                errors.append(f"{label}: scope missing from visible description")
            seen = set()
            for parameter in operation.get("parameters", []):
                key = (parameter["in"], parameter["name"])
                if key in seen:
                    errors.append(f"{label}: duplicate parameter {key}")
                seen.add(key)
                if not parameter.get("description"):
                    errors.append(f"{label}: undescribed parameter {key}")
                if "example" in parameter:
                    check_example(parameter["schema"], parameter["example"], f"{label} {key}")
            media = list(operation.get("requestBody", {}).get("content", {}).values())
            for code, response in operation["responses"].items():
                if code.startswith("2") and code != "204":
                    if not response.get("content"):
                        errors.append(f"{label}: success {code} missing media type")
                    for mime, body in response.get("content", {}).items():
                        schema = resolve(body.get("schema", {}))
                        if not schema:
                            errors.append(f"{label}: success {code} has empty schema")
                        if schema.get("type") == "object" and not schema.get("properties"):
                            errors.append(f"{label}: success {code} is a generic object")
                        if schema.get("type") == "array" and not resolve(schema.get("items", {})).get("properties"):
                            errors.append(f"{label}: success {code} lacks typed array items")
                media.extend(response.get("content", {}).values())
            for body in media:
                if "example" in body:
                    check_example(body.get("schema", {}), body["example"], f"{label} media example")
    if len(set(operations)) != len(operations):
        errors.append("Duplicate operation IDs")
    def collect(value):
        if isinstance(value, dict):
            reference = value.get("$ref")
            if reference and (not reference.startswith("#/components/schemas/") or reference.rsplit("/", 1)[-1] not in components):
                errors.append(f"Unresolved reference: {reference}")
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)
    collect(document)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"PASS: {len(operations)} GA operations, {len(document['paths'])} paths, {len(components)} schemas, {examples} validated examples, all refs/scopes/parameters checked")

def check_live(document):
    provenance = document["x-documentation-provenance"]
    def get(url):
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.load(response)
    current = get(provenance["source"])
    health = get("https://partner-api.marko.fr/health")
    if digest(current) != provenance["public_contract_sha256"]:
        raise SystemExit("Public contract changed: re-export native schemas from the served backend and review response_contracts.py")
    if health.get("git_sha") != provenance["backend_sha"]:
        raise SystemExit("Served backend SHA changed: verify relevant models/serializers before updating documentation provenance")
    print("PASS: public catalogue and served backend match documentation provenance")

parser = argparse.ArgumentParser()
parser.add_argument("--live", action="store_true")
parser.add_argument("--write-download", action="store_true")
args = parser.parse_args()
document = json.loads((ROOT / "openapi.json").read_text())
check(document)
download = json.dumps({"format": "marko-documentation/v1", "markdown": build_download(document)}, ensure_ascii=False, indent=2) + "\n"
target = ROOT / "downloads" / "marko-documentation.json"
if args.write_download:
    target.parent.mkdir(exist_ok=True)
    target.write_text(download)
elif not target.exists() or target.read_text() != download:
    raise SystemExit("Complete documentation download is stale; run --write-download")
if args.live:
    check_live(document)
