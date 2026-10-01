"""Reviewed public dict/stream serializers at the SHA recorded in openapi.json.

Sources: routers/workflows.py, routers/reporting_templates.py,
routers/notifications.py, services/workflow_recommendation_service.py,
services/privacy_export_service.py, services/rgpd_service.py and
services/privacy_case_service.py. Do not infer these responses from examples.
"""
from copy import deepcopy

S = {"type": "string"}
I = {"type": "integer"}
N = {"type": "number"}
B = {"type": "boolean"}
U = {"type": "string", "format": "uuid"}
D = {"type": "string", "format": "date-time"}
NULL = {"type": "null"}
JSON = {"description": "Valeur JSON variable selon la source ou le preset; aucun schéma fixe n'est imposé par cette route."}
MAP = {"type": "object", "additionalProperties": True, "description": "Objet JSON métier; les clés dépendent de la source ou du preset."}

def array(item):
    return {"type": "array", "items": deepcopy(item)}

def nullable(item):
    return {"anyOf": [deepcopy(item), NULL]}

def obj(properties, optional=()):
    return {"type": "object", "properties": deepcopy(properties), "required": [key for key in properties if key not in optional]}

def ref(name):
    return {"$ref": f"#/components/schemas/{name}"}

def page(item):
    return obj({"items": array(item), "total": I, "limit": I, "offset": I})

def contracts(native):
    schemas = {}
    overrides = {}
    def register(name, schema, routes):
        schemas[name] = schema
        for method, path in routes:
            overrides[(method, path)] = ref(name)

    extras = native["x-documentation-extra-models"]
    for key, routes in {
        "comments_list": [("get", "/operations/{operation_id}/comments")],
        "comment": [("post", "/operations/{operation_id}/comments"), ("put", "/comments/{comment_id}")],
        "chronicle": [("get", "/operations/{operation_id}/chronicle")],
        "chronicle_narrative": [("get", "/operations/{operation_id}/chronicle/narrative")],
    }.items():
        for route in routes:
            overrides[route] = extras[key]

    register("NotificationReadAllResult", obj({"marked_read": I}), [("post", "/notifications/actions/read-all")])
    register("ReportingTemplatePage", page(ref("ReportingTemplateResponse")), [("get", "/reporting/templates")])

    definition = obj({
        "id": {**S, "description": "Clé du workflow, pas nécessairement un UUID."},
        "name": S, "description": S, "type": S, "schedule": S, "enabled": B,
        "custom": B, "editable": B, "deletable": B, "toggleable": B,
        "source": S, "scope": S, "impact": S, "job_types": array(S),
        "preset_key": nullable(S), "status": S, "schedule_kind": nullable(S),
        "schedule_config": MAP, "config": MAP,
        "last_run_at": nullable(D), "next_run_at": nullable(D), "last_error": nullable(S),
    })
    register("WorkflowDefinition", definition, [
        ("post", "/workflows/{workflow_id}/actions/toggle"),
        ("post", "/workflows/workflow-definitions"),
        ("put", "/workflows/workflow-definitions/{definition_id}"),
        ("post", "/workflows/recommendations/{recommendation_id}/create-workflow"),
    ])
    overrides[("get", "/workflows")] = array(ref("WorkflowDefinition"))

    preset_field = obj({
        "key": S, "label": S, "type": S, "required": B,
        "placeholder": S, "help": S, "options": array(obj({"value": S, "label": S})),
    }, optional=("placeholder", "help", "options"))
    register("WorkflowPreset", obj({
        "key": S, "label": S, "type": S, "scope": S, "impact": S,
        "default_schedule_kind": S, "default_schedule_config": MAP,
        "config_defaults": MAP, "fields": array(preset_field),
    }), [])
    overrides[("get", "/workflows/presets")] = array(ref("WorkflowPreset"))

    run = obj({
        "id": U, "workflow_id": S, "workflow_name": nullable(S),
        "workflow_source": {"type": "string", "const": "custom"},
        "job_type": nullable(S), "preset_key": nullable(S), "status": S,
        "entity_type": nullable(S), "entity_id": nullable(U), "retry_count": I,
        "error_message": nullable(S), "result": MAP,
        "created_at": nullable(D), "started_at": nullable(D), "completed_at": nullable(D), "trigger_mode": S,
    })
    schemas["WorkflowRun"] = run
    job = obj({
        "id": U, "workflow_id": NULL, "workflow_name": NULL,
        "workflow_source": {"type": "string", "const": "system"},
        "job_type": ref("JobType"), "preset_key": NULL, "status": ref("JobStatus"),
        "entity_type": nullable(S), "entity_id": nullable(U), "retry_count": I,
        "error_message": nullable(S), "result": MAP,
        "document_id": nullable(S), "operation_id": nullable(S), "filename": nullable(S), "document_type": nullable(S),
        "suggestions_count": nullable(I), "pending_suggestions": nullable(I), "applied_suggestions": nullable(I),
        "summary": JSON, "created_at": nullable(D), "started_at": nullable(D), "completed_at": nullable(D),
    })
    register("ProcessingJobHistoryItem", job, [("post", "/workflows/ai-extraction-jobs")])
    register("WorkflowRunAccepted", obj({"workflow": ref("WorkflowDefinition"), "run": ref("WorkflowRun")}), [("post", "/workflows/workflow-definitions/{definition_id}/run")])
    register("WorkflowHistoryPage", page({"anyOf": [ref("WorkflowRun"), ref("ProcessingJobHistoryItem")]}), [("get", "/workflows/history")])
    register("WorkflowStats", obj({key: I for key in (
        "total", "completed", "failed", "running", "pending", "workflows_count",
        "custom_workflows_count", "draft_workflows_count", "inactive_workflows_count",
    )}), [("get", "/workflows/stats")])

    recommendation = obj({
        "id": {**S, "description": "UUID après matérialisation; identifiant preview-* dans une prévisualisation."},
        "scope_type": S, "scope_id": nullable(U), "bundle_key": S, "bundle_label": S,
        "workflow_key": S, "workflow_label": S, "workflow_type": S,
        "title": S, "description": S, "expected_impact": S, "score": N, "confidence": N,
        "priority": {"type": "string", "enum": ["critical", "recommended", "optional"]},
        "priority_label": S, "reason_codes": array(S),
        "evidence": array({"type": "object", "additionalProperties": True, "description": "Éléments de preuve spécifiques au générateur de la recommandation."}),
        "prefill": MAP, "status": S,
        "accepted_at": nullable(D), "dismissed_at": nullable(D), "snoozed_until": nullable(D),
        "created_workflow_key": nullable(S), "workflow_created_at": nullable(D),
        "feedback": MAP, "impact_metrics": MAP, "note": nullable(S),
    }, optional=("accepted_at", "dismissed_at", "snoozed_until", "created_workflow_key", "workflow_created_at", "note"))
    register("WorkflowRecommendation", recommendation, [
        ("post", "/workflows/recommendations/materialize"),
        *[("post", f"/workflows/recommendations/{{recommendation_id}}/{action}") for action in ("accept", "dismiss", "snooze")],
    ])
    schemas["RecommendationBundle"] = obj({
        "key": S, "label": S, "summary": S, "items": array(ref("WorkflowRecommendation")),
        "critical_count": I, "recommended_count": I, "optional_count": I,
    })
    schemas["RecommendationKPIs"] = obj({
        "recommendations_total": I, "recommendation_acceptance_rate": N,
        "recommendation_dismiss_rate": N, "recommendation_snooze_rate": N,
        "time_to_activation_after_recommendation_hours": nullable(N), "prefill_edit_rate": N,
        "workflow_disabled_soon_after_activation_rate": N, "workflow_utility_score": N,
        "monthly_false_positive_count": I, "monthly_false_negative_proxy_count": I,
    })
    register("WorkflowRecommendations", obj({
        "scope_type": S, "scope_id": nullable(U), "scope_label": S, "generated_at": D,
        "items": array(ref("WorkflowRecommendation")), "bundles": array(ref("RecommendationBundle")),
        "kpis": ref("RecommendationKPIs"),
    }), [("get", "/workflows/recommendations"), ("post", "/workflows/recommendations/preview")])

    register("DelegatedErasureResult", obj({
        "privacy_case_id": U, "status": {"type": "string", "enum": native["x-documentation-privacy-statuses"]},
        "result_mode": {"type": "string", "const": "metadata_only"},
        "reconciliation_required": B, "manual_review_required": B,
        "certificate_reference": nullable(S), "completed_at": nullable(D),
        "actions": array({"type": "string", "enum": ["delegated_erasure_completed", "delegated_erasure_blocked", "delegated_erasure_reconciliation_pending"]}), "replayed": B,
    }), [("delete", "/users/me/rgpd/erasure")])
    inventory_entry = obj({
        "table": S, "fields": array(S), "pii_fields": array(S), "has_data": B,
        "pseudonymous_fields": array(S), "excluded_from_export": array(S), "retention": S,
    }, optional=("pseudonymous_fields", "excluded_from_export", "retention"))
    table_count = obj({"has_data": nullable(B), "count": nullable(I), "warning": nullable(S)})
    entity_inventory = obj({
        "scope": S, "entity_slugs": array(S), "warnings": array(S),
        "tables_with_user_references": array(S), "note": S,
        "entities": array(obj({
            "entity_slug": S, "data_environment": S, "status": S, "warnings": array(S),
            "tables": {"type": "object", "additionalProperties": table_count},
        })),
    })
    register("DelegatedDataInventory", obj({
        "user_id": S, "auth_database": {"type": "object", "additionalProperties": inventory_entry},
        "entity_databases": entity_inventory,
    }), [("get", "/users/me/rgpd/inventory")])

    source_manifest = obj({
        "source": S, "required": B, "status": S, "record_count": I, "page_count": I,
        "page_size": I, "data_scope": S, "coverage": S, "excluded_fields": array(S),
        "error_code": nullable(S), "detected_record_count": nullable(I),
    })
    manifest = obj({
        "schema_version": S, "scope_version": S, "requested_entity_slug": S,
        "requested_data_environment": S, "data_scopes": array(S), "generated_at": D,
        "complete": B, "required_source_count": I, "completed_required_source_count": I,
        "failed_required_sources": array(S), "sources": array(source_manifest), "limitations": array(S),
        "manifest_sha256": S, "privacy_case_status": S, "final_status_after_delivery": S,
        "case_finalization_pending": B, "certificate_reference": NULL, "temporary_download_url": NULL,
    })
    register("DelegatedPrivacyExport", obj({
        "schema_version": {"type": "string", "const": "marko_privacy_export/v2"},
        "scope_version": S, "personal_source_registry_version": S, "export_id": U,
        "export_date": D, "user_id": S, "data_environment": S,
        "profile": {"anyOf": [native["x-documentation-privacy-profile"], {"type": "object", "maxProperties": 0}]},
        "preferences": MAP, "notifications": {"type": "array", "maxItems": 0, "items": JSON},
        "audit_entries": {"type": "array", "maxItems": 0, "items": JSON},
        **native["x-documentation-privacy-central"],
        "entity_databases": obj({
            "scope": S, "entity_slugs": array(S), "data_environment": S,
            "entities": array(obj({
                "entity_slug": S, "tables": obj(native["x-documentation-privacy-tables"]), "status": S,
            })),
        }),
        "manifest": manifest,
    }), [("get", "/users/me/rgpd/export")])
    return schemas, overrides
