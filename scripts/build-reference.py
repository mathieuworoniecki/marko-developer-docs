#!/usr/bin/env python3
"""Combine the public GA catalogue with reviewed runtime-matching schemas.

The public catalogue owns visibility, operation IDs, scopes, security, servers
and mandatory partner headers. Native models own payload/parameter types. The
reviewed dict serializers supply responses without Pydantic response models.
"""
import argparse
from copy import deepcopy
import hashlib
from http import HTTPStatus
import json
from pathlib import Path
import re
import sys
from jsonschema import Draft202012Validator, FormatChecker

from response_contracts import contracts
from field_descriptions import enrich_fields

METHODS = {"get", "post", "put", "patch", "delete"}
TAG_LABELS = {
    "auth": "Authentification", "entity": "Entité", "portfolio": "Portefeuille",
    "deals": "Deals", "fonds": "Fonds", "spvs": "SPV", "operations": "Opérations",
    "taxonomies": "Taxonomies", "import-jobs": "Imports par lot", "comments": "Commentaires",
    "documents": "Documents", "users": "Utilisateurs", "settings": "Paramètres",
    "rcci": "Conformité RCCI", "field-definitions": "Champs métier", "search": "Recherche",
    "operateurs": "Opérateurs", "alerts": "Alertes", "notifications": "Notifications",
    "calendar": "Calendrier", "enrichment": "Enrichissement SIREN", "reports": "Exports",
    "reporting": "Templates de reporting", "workflows": "Workflows et extraction IA", "tasks": "Tâches",
}
DESCRIPTIONS = {
    "limit": "Nombre maximal de résultats sur cette page; bornes et valeur par défaut ci-dessous.",
    "offset": "Nombre de résultats à ignorer avant cette page (commence à 0).",
    "page": "Numéro de page; consultez la valeur minimale et la valeur par défaut de cette route.",
    "id": "Identifiant MARKO de la ressource.",
    "external_id": "Identifiant stable de votre système, dans le contexte de votre intégration.",
    "existing_marko_id": "UUID d'une ressource MARKO existante à associer lors du premier upsert externe; la cible doit être accessible et compatible.",
    "marko_id": "Identifiant MARKO résolu ou créé; conservez-le pour les appels ultérieurs.",
    "operation_external_id": "Identifiant externe de l'opération, appartenant à la même intégration.",
    "operation_id": "UUID MARKO de l'opération.", "spv_id": "UUID MARKO de la SPV.",
    "fond_id": "UUID MARKO du fonds.", "operateur_id": "UUID MARKO de l'opérateur.",
    "document_id": "UUID MARKO du document.", "user_id": "Identifiant utilisateur MARKO; il n'est pas nécessairement un UUID.",
    "job_id": "UUID du job durable à suivre.", "items": "Résultats de la page courante.",
    "total": "Nombre total de résultats correspondant aux filtres.", "version": "Version de la ressource MARKO.",
    "source_created_at": "Date de création dans le système source, avec fuseau horaire.",
    "source_updated_at": "Date de dernière mise à jour dans le système source, avec fuseau horaire. Pour une note déjà versionnée, un changement exige une date strictement plus récente.",
    "taxonomy_additions": "Options de taxonomie créées par cet upsert. Conservez les codes retournés; le suffixe custom__ n'est pas prévisible.",
    "data": "Données métier de l'opération. Consultez GET /field-definitions pour les clés, types et unités disponibles; ne déduisez pas les unités des noms.",
    "category": "Catégorie de la note; les règles exactes dépendent de la route. Pour l'import externe: chaîne de 1 à 80 caractères, libre par défaut.",
    "description_i18n": "Textes par locale normalisée (fr, en, fr-fr…); contraintes complémentaires dans le guide Imports et notes.",
    "date": "Date métier; le type et le format ci-dessous font autorité pour cette route.",
    "created_at": "Date de création au format ISO 8601.", "updated_at": "Date de dernière modification au format ISO 8601.",
    "completed_at": "Date de fin, lorsqu'une exécution ou un traitement est terminé.",
    "error_code": "Code exploitable pour diagnostiquer un échec; consulter aussi error_message.",
    "error_message": "Détail de l'échec, lorsqu'il est disponible.",
    "nonce": "Valeur aléatoire unique pour cet échange; ne jamais réutiliser un nonce avec la même clé.",
    "timestamp": "Heure Unix en secondes de l'échange signé.",
    "key_id": "Identifiant public de la clé; utiliser la valeur réelle fournie par l'administrateur.",
    "signature": "HMAC-SHA256 hexadécimal du message canonique à quatre lignes; voir Authentification.",
    "access_token": "Bearer de courte durée à utiliser dans Authorization.",
    "expires_in": "Durée du bearer en secondes; utilisez la valeur retournée plutôt qu'une durée fixe.",
    "environment": "Environnement de données associé à la clé; distinct de l'hôte d'infrastructure.",
    "entity_slug": "Entité à laquelle l'intégration est rattachée.",
    "confirm": "Confirmation explicite exigée pour cette action; le scope seul ne remplace pas cette confirmation.",
    "only_high_priority": "Limiter aux recommandations de priorité élevée.",
    "include_dismissed": "Inclure les recommandations classées comme non pertinentes.",
    "template_type": "Filtrer les templates par type.",
    "scope_type": "Périmètre auquel la recommandation ou l'objet se rapporte.",
    "name": "Nom de la ressource. Les recherches exactes et partielles sont décrites au niveau de la route.",
    "search": "Texte de recherche selon les règles de cette route.",
    "file": "Fichier binaire envoyé dans multipart/form-data; ne pas encoder en Base64.",
    "filename": "Nom du fichier.",
    "notes": "Notes historiques de l'opération. Le lot complet accepte au maximum 10 000 notes.",
    "operations": "Opérations à importer; entre 1 et 500 par lot, enveloppe normalisée limitée à 20 Mio.",
    "mode": "Mode de traitement accepté par cette route.",
    "enabled": "Indique si cette définition est activée.",
    "result": "Résultat public de l'exécution; structure variable selon le preset ou le type de job.",
    "workflow_id": "Clé du workflow; certaines routes utilisent une chaîne, d'autres un UUID. Respectez le type de cette route.",
    "request_id": "Identifiant de corrélation pour le diagnostic de la requête.",
    "siren": "SIREN français sur 9 chiffres; le service vérifie aussi le checksum lorsque la route le prévoit.",
}
EXAMPLE_FIELDS = {
    "key_id": "examplekey01", "nonce": "example_nonce_unique_01", "signature": "0" * 64,
    "email": "integration@example.com", "name": "Exemple MARKO", "text": "Note de suivi synthétique.",
    "external_id": "crm-example-001", "category": "libre", "status": "instruction",
    "phase": "p03_financement", "scope_type": "entity", "priority": "recommended",
    "siren": "732829320", "source_updated_at": "2026-10-01T10:00:00Z",
    "filename": "exemple.pdf", "content_type": "application/pdf", "token_type": "Bearer",
}

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def enrich(public, native):
    result = deepcopy(public)
    result["openapi"] = "3.1.0"
    tags = {tag["name"]: deepcopy(tag) for tag in result.get("tags", [])}
    for item in result["paths"].values():
        for method, operation in item.items():
            if method in METHODS:
                for name in operation.get("tags", []):
                    tags.setdefault(name, {"name": name})["x-group"] = TAG_LABELS[name]
    result["tags"] = list(tags.values())
    native_schemas = native["components"]["schemas"]
    manual, overrides = contracts(native)
    components = result.setdefault("components", {}).setdefault("schemas", {})
    components.update(deepcopy(native_schemas))
    components.update(manual)
    # Serializer helpers reuse primitive schema objects. Give each property its
    # own JSON node before attaching field-specific editorial descriptions.
    components = json.loads(json.dumps(components, ensure_ascii=False))
    result["components"]["schemas"] = components
    # Runtime validators and service checks not represented by Pydantic's basic
    # JSON Schema. These are reviewed rules of the served version.
    for name in ("ExternalNoteUpsertRequest", "ExternalNoteImport"):
        model = components.get(name)
        if not model:
            continue
        model["description"] = "Note historique. text ou description_i18n non vide est requis. Dates source avec fuseau horaire; source_updated_at ne peut pas précéder source_created_at. Voir Imports et notes pour les règles de traduction et de version."
        model["anyOf"] = [
            {"required": ["text"], "properties": {"text": {"type": "string", "minLength": 1}}},
            {"required": ["description_i18n"], "properties": {"description_i18n": {"type": "object", "minProperties": 1}}},
        ]
        model["properties"]["date"] = {"anyOf": [{"type": "string", "format": "date-time"}, {"type": "string", "format": "date"}], "description": "Date métier avec fuseau horaire, ou date YYYY-MM-DD normalisée à minuit UTC."}
        model["properties"]["description_i18n"] = {"anyOf": [
            {"type": "object", "maxProperties": 20, "additionalProperties": {"type": "string", "minLength": 1, "maxLength": 10000}},
            {"type": "null"},
        ], "description": "Au plus 20 locales et 100 000 caractères au total. Locales normalisées en minuscules avec tirets, max 35 caractères; aucune collision après normalisation. Les textes vides sont refusés."}
    for name in ("ExternalDocumentCreateRequest", "Body_upload_document_public_documents_external__external_id__upload_put"):
        model = components[name]
        model["anyOf"] = [
            {"required": ["operation_id"], "properties": {"operation_id": {"type": "string", "format": "uuid"}}},
            {"required": ["operation_external_id"], "properties": {"operation_external_id": {"type": "string", "minLength": 1}}},
        ]
        model["description"] = "Une opération est requise: fournir operation_id ou operation_external_id. Lorsque les deux sont fournis, operation_id est utilisé. Pour un upload de fichier, appeler directement /upload avec un nouvel external_id; une déclaration metadata préalable peut être renvoyée sans ajout de fichier."
    upload = components["Body_upload_document_public_documents_external__external_id__upload_put"]["properties"]
    upload["file"]["format"] = "binary"
    upload["partner_metadata"]["description"] = "Chaîne contenant un objet JSON valide. Au niveau multipart, ce champ est du texte; il est ensuite décodé en objet."
    view_rules = native["x-documentation-saved-view-constraints"]
    for name in ("SavedViewCreate", "SavedViewUpdate"):
        model = components[name]
        nullable_view = name == "SavedViewUpdate"
        def view_field(schema):
            return {"anyOf": [schema, {"type": "null"}]} if nullable_view else schema
        model["properties"]["icon"] = view_field({"type": "string", "enum": view_rules["icons"]})
        model["properties"]["color"] = view_field({"type": "string", "enum": view_rules["colors"]})
        model["properties"]["filters"] = view_field({"type": "object", "maxProperties": 24, "propertyNames": {"pattern": "^[a-z][a-z0-9_]{0,63}$"}, "additionalProperties": True, "description": "État de filtre; pour une vue operations, seules les clés décrites par le contrat conditionnel de création sont acceptées."})
        model["properties"]["columns"] = view_field({"type": "array", "maxItems": 64, "items": {"type": "string", "pattern": "^[a-z][a-z0-9_]{0,63}$"}})
        model["properties"]["sort"] = view_field({"type": "object", "maxProperties": 4, "propertyNames": {"pattern": "^[a-z][a-z0-9_]{0,63}$"}, "additionalProperties": True})
        model["description"] = "État de vue limité à 16 384 octets JSON pour filters, columns et sort. Le nom est normalisé et doit rester non vide. Les allowlists operations sont contrôlées selon le type de la vue, y compris lors d'un update."
        if not nullable_view:
            model["allOf"] = [{
                "if": {"required": ["entity_type"], "properties": {"entity_type": {"const": "operations"}}},
                "then": {"properties": {
                    "filters": {"propertyNames": {"enum": view_rules["operation_filters"]}},
                    "columns": {"items": {"type": "string", "enum": view_rules["operation_columns"]}},
                    "sort": {"type": "object", "additionalProperties": False, "properties": {
                        "sort_by": {"type": "string", "enum": view_rules["operation_sort"]},
                        "sort_order": {"type": "string", "enum": ["asc", "desc"]},
                    }},
                }},
            }]
    # JobType is used by an untyped serializer, not a native response model.
    if "JobType" not in components:
        components["JobType"] = {"type": "string", "enum": ["ai_extraction", "ai_categorization", "kpi_calculation", "echeancier_generation"], "description": "Type du job de traitement système."}
    metadata = {
        "backend_sha": native["x-documentation-source-sha"],
        "public_contract_sha256": digest(public),
        "source": "https://partner-api.marko.fr/v1/openapi.json",
        "schema_source": "Runtime-matching Pydantic models and reviewed public serializers",
    }
    result["x-documentation-provenance"] = metadata
    result["info"]["description"] += "\n\nRéférence enrichie pour les développeurs et les assistants IA. Exemples synthétiques; les champs sont extraits des modèles et sérialiseurs de la version indiquée dans x-documentation-provenance."
    for path, item in result["paths"].items():
        for method, operation in item.items():
            if method not in METHODS:
                continue
            native_op = native["paths"].get(path, {}).get(method)
            if native_op is None:
                raise ValueError(f"Public route absent from verified backend: {method} {path}")
            for parameter in operation.get("parameters", []):
                match = next((p for p in native_op.get("parameters", []) if p["name"] == parameter["name"] and p["in"] == parameter["in"]), None)
                if match and parameter["in"] != "header":
                    old = parameter.get("schema", {})
                    parameter["schema"] = deepcopy(match["schema"])
                    # Keep catalogue constraints when the handler simply accepts a
                    # string and validates it later inside the service.
                    for key in ("pattern", "minLength", "maxLength", "format", "enum"):
                        if key in old and key not in parameter["schema"]:
                            parameter["schema"][key] = old[key]
                    parameter["required"] = match.get("required", False)
                    if match.get("description"):
                        parameter.setdefault("description", match["description"])
                if not parameter.get("description"):
                    parameter["description"] = DESCRIPTIONS.get(parameter["name"], f"Paramètre {parameter['name']} pour cette route; type, format et contraintes ci-dessous.")
                if path.endswith("/chronicle") and parameter["name"] == "entry_type":
                    parameter["schema"] = {"anyOf": [{"$ref": "#/components/schemas/ChronicleEntryType"}, {"type": "null"}]}
                if path.endswith("/chronicle/narrative") and parameter["name"] == "category":
                    parameter["schema"] = {"anyOf": [{"$ref": "#/components/schemas/OperationChronicleCategory"}, {"type": "null"}]}
                if path == "/workflows/recommendations" and parameter["name"] == "scope_type":
                    parameter["schema"]["enum"] = ["entity", "fund", "spv", "operation"]
            known = {(p["name"], p["in"]) for p in operation.get("parameters", [])}
            for parameter in native_op.get("parameters", []):
                if (parameter["name"], parameter["in"]) not in known and parameter["in"] in ("query", "path"):
                    operation.setdefault("parameters", []).append(deepcopy(parameter))
            if path.startswith("/users/me"):
                for header in ("X-Marko-Delegated-User-Id", "X-Marko-Delegated-User-Email"):
                    operation.setdefault("parameters", []).append({
                        "name": header, "in": "header", "required": False, "schema": {"type": "string"},
                        "description": "Fournir exactement un des deux headers de délégation (Id ou Email), dans la même entité. Ils sont mutuellement exclusifs. Voir le guide Scopes et délégation.",
                    })
            for parameter in operation.get("parameters", []):
                parameter.setdefault("description", DESCRIPTIONS.get(parameter["name"], f"Paramètre {parameter['name']} de cette route; contraintes ci-dessous."))
            if native_op.get("requestBody"):
                old_body = operation.get("requestBody", {})
                operation["requestBody"] = deepcopy(native_op["requestBody"])
                for mime, media in operation["requestBody"].get("content", {}).items():
                    previous = old_body.get("content", {}).get(mime, {})
                    if "example" in previous:
                        media["example"] = previous["example"]
                # The public fixtures passed JSON shape but failed the actual
                # backend validators; keep these explicitly reviewed corrections.
                example = operation["requestBody"]["content"].get("application/json", {}).get("example")
                if method == "post" and path == "/operateurs" and isinstance(example, dict):
                    example["siren"] = "732829320"
                if method == "post" and path == "/users/me/saved-views" and isinstance(example, dict):
                    example["name"] = "Vue exemple"
                    example["filters"] = {}
                if method == "post" and path == "/workflows/ai-extraction-jobs" and isinstance(example, dict):
                    # Ignored by the real body model: it is not a dry-run flag.
                    example.pop("run_now", None)
            native_success = {code: response for code, response in native_op["responses"].items() if code.startswith("2") and code != "204"}
            for code in native.get("x-documentation-error-statuses", {}).get(f"{method} {path}", []):
                operation["responses"].setdefault(str(code), {
                    "description": HTTPStatus(code).phrase + " — refus déclaré dans le handler ou un helper de cette route.",
                    "content": {"application/problem+json": {"schema": {"$ref": "#/components/schemas/ProblemDetails"}}},
                })
            if method == "put" and path in ("/documents/external/{external_id}", "/documents/external/{external_id}/upload"):
                operation["responses"]["201"] = deepcopy(operation["responses"]["200"])
                operation["responses"]["201"]["description"] = "Document créé; conserve son identifiant externe et son document_id."
                operation["responses"]["200"]["description"] = "Référence documentaire existante ou réponse rejouée."
            if method == "delete" and path == "/users/{user_id}":
                operation["responses"]["200"] = deepcopy(operation["responses"]["202"])
                operation["responses"]["200"]["description"] = "Invitation non activée annulée immédiatement."
                operation["responses"]["202"]["description"] = "Retrait d'accès et effacement durable acceptés pour un compte actif."
            if path == "/users/me/rgpd/erasure":
                operation["responses"]["202"] = {"description": "Effacement durable accepté; le dossier n'est pas encore terminé.", "content": {"application/json": {}}}
                operation["responses"]["200"]["description"] = "Dossier d'effacement terminé; réponse limitée aux métadonnées."
            for code, response in operation["responses"].items():
                if not code.startswith("2") or code == "204":
                    continue
                replacement = overrides.get((method, path))
                if replacement is None:
                    model_response = native_success.get(code) or next(iter(native_success.values()), {})
                    replacement = model_response.get("content", {}).get("application/json", {}).get("schema")
                if replacement is not None:
                    response.setdefault("content", {}).setdefault("application/json", {})["schema"] = deepcopy(replacement)
                if method == "get" and path in ("/fonds", "/spvs"):
                    response.setdefault("headers", {}).update({
                        "X-Marko-Limit": {"schema": {"type": "integer"}, "description": "Limite appliquée à la page."},
                        "X-Marko-Offset": {"schema": {"type": "integer"}, "description": "Offset appliqué à la page."},
                        "X-Marko-Has-More": {"schema": {"type": "boolean"}, "description": "true si une page suivante existe."},
                    })
                if path == "/users/me/rgpd/export":
                    response.setdefault("headers", {}).update({
                        "Content-Disposition": {"schema": {"type": "string"}, "description": "attachment; filename=marko_rgpd_export.json"},
                        "Cache-Control": {"schema": {"type": "string"}, "description": "no-store"},
                        "X-Marko-Export-Schema": {"schema": {"type": "string"}, "description": "marko_privacy_export/v2"},
                        "X-Marko-Privacy-Case-Id": {"schema": {"type": "string", "format": "uuid"}, "description": "Identifiant du dossier associé à cet export."},
                    })
                if (method, path) in {
                    ("post", "/users/{user_id}/actions/suspend"), ("post", "/users/{user_id}/actions/unsuspend"),
                    ("delete", "/users/{user_id}"), ("delete", "/users/me/rgpd/erasure"),
                    ("post", "/enrichment/siren/{siren}/resolve"), ("post", "/workflows/workflow-definitions/{definition_id}/run"),
                    ("post", "/workflows/ai-extraction-jobs"),
                }:
                    response.setdefault("headers", {}).update({
                        "Idempotency-Key": {"schema": {"type": "string"}, "description": "Clé d'idempotence utilisée pour l'action."},
                        "X-Marko-Idempotency-Key-Source": {"schema": {"type": "string", "enum": ["client", "server"]}, "description": "Origine de la clé utilisée."},
                        "X-Marko-Idempotency-TTL-Seconds": {"schema": {"type": "integer"}, "description": "Durée de rétention annoncée pour cette action, en secondes."},
                    })
            scope = operation.get("x-marko-required-scope")
            description = operation.get("description", "")
            description += f"\n\n**Scope requis :** `{scope}`. [Scopes et délégation](/scopes-and-delegation)." if scope else "\n\nCette route échange la signature HMAC contre un bearer; aucun bearer préalable n'est requis. [Authentification](/authentication)."
            if path.startswith("/users/me"):
                description += "\n\n**Délégation utilisateur :** exactement un header `X-Marko-Delegated-User-Id` ou `X-Marko-Delegated-User-Email`."
                if "/saved-views" in path:
                    capability = "saved_views"
                elif "/custom-dashboards" in path:
                    capability = "custom_dashboards"
                elif "/rgpd/" in path:
                    capability = "rgpd_" + path.rsplit("/", 1)[-1]
                else:
                    capability = "user_self_service"
                description += f"\n\n**Accès complémentaire :** allowlist utilisateur explicite sur la clé et capacité `{capability}`. Le sujet doit être approuvé et appartenir à la même entité."
            if any(p["name"] == "Idempotency-Key" and p.get("required") for p in operation.get("parameters", [])):
                description += "\n\n**Idempotence :** header `Idempotency-Key` obligatoire. Pour reprendre la même mutation, réutiliser la même clé et le même contenu. [Écritures et idempotence](/writes-and-idempotency)."
            if path.startswith("/import-jobs") or path == "/operations/batch":
                description += "\n\n[Import par lot, suivi et reprise](/imports-and-notes)."
            if path.startswith("/documents"):
                description += "\n\n[Documents et upload](/documents-guide)."
            if path.startswith("/workflows"):
                description += "\n\n[Workflows et extraction IA](/workflows-guide)."
            if path.startswith("/users/me/rgpd"):
                description += "\n\n[Export, inventaire et effacement RGPD](/privacy-guide)."
            operation["description"] = description

    # Standard descriptions survive Mintlify's page/Markdown rendering.
    def describe(node):
        if isinstance(node, dict):
            for name, field in node.get("properties", {}).items():
                if name in DESCRIPTIONS and not field.get("description"):
                    field["description"] = DESCRIPTIONS[name]
            if node.get("type") == "object" and not node.get("properties") and node.get("additionalProperties"):
                node.setdefault("description", "Objet JSON extensible. Les types des valeurs sont indiqués par additionalProperties lorsque la route les contraint.")
            for value in node.values():
                describe(value)
        elif isinstance(node, list):
            for value in node:
                describe(value)
    describe(result)

    # Keep only components reachable from GA routes; never ship beta/admin models.
    reachable = set()
    def collect(node):
        if isinstance(node, dict):
            reference = node.get("$ref", "")
            prefix = "#/components/schemas/"
            if reference.startswith(prefix):
                name = reference[len(prefix):]
                if name not in reachable:
                    if name not in components:
                        raise ValueError(f"Missing schema {name}")
                    reachable.add(name)
                    collect(components[name])
            for value in node.values():
                collect(value)
        elif isinstance(node, list):
            for value in node:
                collect(value)
    collect(result["paths"])
    result["components"]["schemas"] = {name: components[name] for name in sorted(reachable)}
    enrich_fields(result)
    repair_examples(result)
    return result

def repair_examples(document):
    """Keep valid catalogue examples; complete/replace stale examples with fixtures.

    Every generated example is synthetic. This verifies JSON shape, not business
    execution or availability of the example's resources in a customer tenant.
    """
    schemas = document["components"]["schemas"]
    checker = FormatChecker()
    def valid(schema, value):
        rooted = {"components": document["components"], **schema}
        return Draft202012Validator(rooted, format_checker=checker).is_valid(value)

    def fixture(schema, old=None, name="", depth=0):
        if depth > 25:
            raise ValueError(f"Recursive required example at {name}")
        if valid(schema, old):
            return old
        if "$ref" in schema:
            return fixture(schemas[schema["$ref"].rsplit("/", 1)[-1]], old, name, depth + 1)
        if "const" in schema:
            return schema["const"]
        if "enum" in schema:
            return schema["enum"][0]
        if "default" in schema and valid(schema, schema["default"]):
            return deepcopy(schema["default"])
        variants = schema.get("anyOf") or schema.get("oneOf")
        if variants:
            for variant in variants:
                candidate = fixture(variant, old, name, depth + 1)
                if valid(schema, candidate):
                    return candidate
            raise ValueError(f"No valid example variant at {name}")
        kind = schema.get("type")
        if kind == "object" or "properties" in schema:
            properties = schema.get("properties", {})
            previous = old if isinstance(old, dict) else {}
            result = {}
            for key, child in properties.items():
                if key in schema.get("required", []) or key in previous:
                    result[key] = fixture(child, previous.get(key), key, depth + 1)
            if schema.get("additionalProperties", True) is not False:
                for key, value in previous.items():
                    if key not in properties:
                        if properties and "additionalProperties" not in schema:
                            continue
                        extra = schema.get("additionalProperties", True)
                        result[key] = fixture(extra, value, key, depth + 1) if isinstance(extra, dict) else value
            return result
        if kind == "array":
            previous = old if isinstance(old, list) else []
            count = max(len(previous), schema.get("minItems", 0))
            count = min(count, schema.get("maxItems", count))
            return [fixture(schema.get("items", {}), previous[i] if i < len(previous) else None, name, depth + 1) for i in range(count)]
        if kind == "boolean":
            return False
        if kind == "null":
            return None
        if kind in ("number", "integer"):
            value = max(0, schema.get("minimum", 0))
            if "exclusiveMinimum" in schema:
                value = max(value, schema["exclusiveMinimum"] + 1)
            if "maximum" in schema:
                value = min(value, schema["maximum"])
            return value
        if kind == "string":
            fmt = schema.get("format")
            formats = {"uuid": "11111111-1111-4111-8111-111111111111", "date-time": "2026-10-01T10:00:00Z", "date": "2026-10-01", "email": "integration@example.com", "uri": "https://example.com/resource", "binary": "<fichier binaire>"}
            candidates = [formats.get(fmt), EXAMPLE_FIELDS.get(name), "example", "examplekey01", "0" * 64, "732829320", "fr", "11111111-1111-4111-8111-111111111111", "#76E7F4", "example@example.com", "Europe/Paris", "09:00"]
            for candidate in candidates:
                if candidate is None:
                    continue
                candidate = candidate[:schema.get("maxLength", len(candidate))]
                candidate += "x" * max(0, schema.get("minLength", 0) - len(candidate))
                if valid(schema, candidate):
                    return candidate
            raise ValueError(f"No valid synthetic string for {name}: {schema}")
        return old

    corrected = 0
    for path, item in document["paths"].items():
        for method, operation in item.items():
            if method not in METHODS:
                continue
            media = list(operation.get("requestBody", {}).get("content", {}).values())
            for response in operation["responses"].values():
                media += list(response.get("content", {}).values())
            for content in media:
                if "example" in content and not valid(content.get("schema", {}), content["example"]):
                    content["example"] = fixture(content["schema"], content["example"])
                    if not valid(content["schema"], content["example"]):
                        raise ValueError(f"Invalid repaired example: {method} {path}")
                    corrected += 1
            for parameter in operation.get("parameters", []):
                if "example" in parameter and not valid(parameter["schema"], parameter["example"]):
                    parameter["example"] = fixture(parameter["schema"], parameter["example"], parameter["name"])
                    corrected += 1
    print(f"Corrected {corrected} stale examples against the actual typed schemas")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("openapi.json"))
    args = parser.parse_args()
    result = enrich(json.loads(args.public.read_text()), json.loads(args.native.read_text()))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"Generated {sum(method in METHODS for item in result['paths'].values() for method in item)} public operations; {len(result['components']['schemas'])} reachable schemas")

if __name__ == "__main__":
    main()
