#!/usr/bin/env python3
"""Verify the published contract, examples, documentation and optional live drift."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import urllib.request
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
METHODS = {"get", "post", "put", "patch", "delete"}

BASE_GUIDES = ["authentication", "environments", "errors-and-retries", "scopes-and-delegation"]
FAMILY_GUIDES = {
    "auth": ["quickstart", "code-examples"],
    "operations": ["concepts", "writes-and-idempotency", "pagination-and-data", "taxonomies-guide", "imports-and-notes", "tutorials/crm-sync"],
    "documents": ["concepts", "documents-guide", "tutorials/document-extraction"],
    "import-jobs": ["imports-and-notes", "tutorials/batch-import"],
    "workflows": ["workflows-guide", "tutorials/document-extraction"],
    "taxonomies": ["taxonomies-guide"],
    "field-definitions": ["pagination-and-data", "taxonomies-guide"],
    "users": ["privacy-guide"],
    "fonds": ["concepts", "pagination-and-data", "writes-and-idempotency"],
    "spvs": ["concepts", "pagination-and-data", "writes-and-idempotency"],
    "operateurs": ["concepts", "pagination-and-data", "writes-and-idempotency"],
}
TUTORIAL_PACKS = {
    "crm-sync": {
        "title": "CRM vers MARKO", "guides": ["tutorials/crm-sync", "concepts", "writes-and-idempotency", "imports-and-notes", "taxonomies-guide"],
        "paths": ["/auth/token", "/operations/external/{external_id}", "/operations/external/{operation_external_id}/notes/external/{note_external_id}", "/taxonomies"],
    },
    "batch-import": {
        "title": "Import par lot", "guides": ["tutorials/batch-import", "imports-and-notes", "writes-and-idempotency"],
        "tags": ["import-jobs"], "paths": ["/auth/token", "/operations/batch"],
    },
    "document-extraction": {
        "title": "Document et extraction IA", "guides": ["tutorials/document-extraction", "documents-guide", "workflows-guide"],
        "paths": ["/auth/token", "/documents/external/{external_id}/upload", "/documents/{document_id}", "/workflows/ai-extraction-jobs", "/workflows/ai-extraction-jobs/{job_id}"],
    },
}

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def build_download(document, pages=None, title="Documentation complète"):
    config = json.loads((ROOT / "docs.json").read_text())
    pages = pages or [page for group in config["navigation"]["groups"] for page in group.get("pages", [])]
    sections = [f"# MARKO — {title}\n\nGuides et référence des opérations publiques stables. Exemples synthétiques.\n"]
    for page in pages:
        content = (ROOT / f"{page}.mdx").read_text()
        parts = content.split("---", 2)
        metadata, body = parts[1], parts[2]
        title = re.search(r'^title:\s*"(.+)"', metadata, re.M).group(1)
        body = re.sub(r'^import .+$', '', body, flags=re.M)
        body = re.sub(r'<CopyDocumentation\b[^>]*?/>', '', body)
        body = re.sub(r'<Card\s+title="([^"]+)"[^>]*href="([^"]+)"[^>]*>(.*?)</Card>', lambda m: f"[{m[1]}]({m[2]}): {m[3].strip()}", body, flags=re.S)
        body = re.sub(r'</?(?:Columns|CodeGroup)\b[^>]*>', '', body)
        sections.append(f"\n# {title}\n\nSource: https://developers.marko.fr/{page}\n{body.strip()}\n")
    sections.append("\n# Contrat OpenAPI complet\n\nLes $ref ci-dessous sont résolus dans components.schemas du même document.\n\n```json\n" + json.dumps(document, ensure_ascii=False, indent=2) + "\n```\n")
    return "\n".join(sections)

def slice_contract(document, select):
    result = deepcopy(document)
    result["paths"] = {
        path: {method: op for method, op in item.items() if method in METHODS and select(path, method, op)}
        for path, item in result["paths"].items()
    }
    result["paths"] = {path: item for path, item in result["paths"].items() if item}
    if not result["paths"]:
        raise ValueError("Empty documentation pack")
    schemas = result["components"]["schemas"]
    reachable = set()
    def collect(value):
        if isinstance(value, dict):
            if "$ref" in value:
                name = value["$ref"].rsplit("/", 1)[-1]
                if name not in reachable:
                    reachable.add(name)
                    collect(schemas[name])
            for child in value.values(): collect(child)
        elif isinstance(value, list):
            for child in value: collect(child)
    collect(result["paths"])
    result["components"]["schemas"] = {name: schemas[name] for name in sorted(reachable)}
    tags = {tag for item in result["paths"].values() for op in item.values() for tag in op.get("tags", [])}
    result["tags"] = [tag for tag in result.get("tags", []) if tag["name"] in tags]
    return result

def download_files(document):
    files = {"marko-documentation": {"format": "marko-documentation/v1", "title": "Documentation complète", "markdown": build_download(document)}}
    index = [{"id": "marko-documentation", "title": "Toute la documentation", "kind": "all"}]
    for tag in document.get("tags", []):
        name = tag["name"]
        title = tag.get("x-group", name)
        contract = slice_contract(document, lambda p, _m, op: name in op.get("tags", []) or p == "/auth/token")
        guides = list(dict.fromkeys(BASE_GUIDES + FAMILY_GUIDES.get(name, ["resources", "pagination-and-data"])))
        files[name] = {"format": "marko-documentation/v1", "title": title, "markdown": build_download(contract, guides, title)}
        index.append({"id": name, "title": title, "kind": "family"})
    for key, topic in TUTORIAL_PACKS.items():
        contract = slice_contract(document, lambda p, _m, op: op["operationId"] in topic.get("operations", []) or p in topic.get("paths", []) or any(t in topic.get("tags", []) for t in op.get("tags", [])))
        assert "/auth/token" in contract["paths"], key + " misses authentication"
        guides = list(dict.fromkeys(BASE_GUIDES + topic["guides"]))
        files[key] = {"format": "marko-documentation/v1", "title": topic["title"], "markdown": build_download(contract, guides, topic["title"])}
        index.append({"id": key, "title": topic["title"], "kind": "tutorial"})
    files["index"] = {"format": "marko-documentation-index/v1", "topics": index}
    return files

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
        for name, field in schema.get("properties", {}).items():
            if not field.get("description"):
                errors.append(f"{schema.get('title', 'schema')}.{name}: field has no description")
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--write-download", action="store_true")
    args = parser.parse_args()
    document = json.loads((ROOT / "openapi.json").read_text())
    check(document)
    files = download_files(document)
    expected = set()
    for name, payload in files.items():
        target = ROOT / "downloads" / f"{name}.json"
        expected.add(target.name)
        content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        if args.write_download:
            target.parent.mkdir(exist_ok=True)
            target.write_text(content)
        elif not target.exists() or target.read_text() != content:
            raise SystemExit(f"Documentation pack {name} is stale; run --write-download")
    extra = {p.name for p in (ROOT / "downloads").glob('*.json')} - expected
    if extra: raise SystemExit(f"Unexpected download files: {sorted(extra)}")
    print(f"PASS: full download, {len(document.get('tags', []))} API families and {len(TUTORIAL_PACKS)} tutorial packs match the reference")
    if args.live: check_live(document)

if __name__ == "__main__":
    main()
