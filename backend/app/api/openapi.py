"""Document middleware-enforced security and the bounded in-memory multipart parser."""

from app.schemas import ErrorEnvelope


def install_openapi(app):
    original = app.openapi

    def schema():
        if app.openapi_schema:
            return app.openapi_schema
        document = original()
        components = document.setdefault("components", {})
        components.setdefault("securitySchemes", {}).update(
            {
                "SessionCookie": {
                    "type": "apiKey",
                    "in": "cookie",
                    "name": "sf_session",
                },
                "CsrfToken": {"type": "apiKey", "in": "header", "name": "X-CSRF-Token"},
            }
        )
        components.setdefault("schemas", {}).setdefault(
            "ErrorEnvelope",
            ErrorEnvelope.model_json_schema(
                ref_template="#/components/schemas/{model}"
            ),
        )
        for path, item in document["paths"].items():
            for method, operation in item.items():
                if method not in ("get", "post", "delete", "put", "patch"):
                    continue
                public = path in (
                    "/api/sessions",
                    "/api/runtime",
                    "/health/live",
                    "/health/ready",
                )
                operation["security"] = (
                    []
                    if public
                    else [
                        {
                            "SessionCookie": [],
                            **(
                                {"CsrfToken": []}
                                if method not in ("get", "head")
                                else {}
                            ),
                        }
                    ]
                )
                for code in (400, 403, 404, 409, 410, 413, 422, 429, 500, 502, 503):
                    if path == "/health/ready" and code == 503:
                        operation.setdefault("responses", {})["503"] = {
                            "description": "Database not ready",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HealthInfo"
                                    }
                                }
                            },
                        }
                        continue
                    operation.setdefault("responses", {})[str(code)] = {
                        "description": "Sanitized application error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorEnvelope"}
                            }
                        },
                    }
                if operation["operationId"] == "uploadMaterial":
                    operation["requestBody"] = {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": ["file"],
                                    "properties": {
                                        "file": {"type": "string", "format": "binary"}
                                    },
                                }
                            }
                        },
                    }
                if operation["operationId"] in ("selectSource", "decideResearchOffer"):
                    name = (
                        "PromotionReceipt"
                        if operation["operationId"] == "selectSource"
                        else "OfferDecision"
                    )
                    operation["responses"]["202"] = {
                        "description": "Accepted for processing",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": f"#/components/schemas/{name}"}
                            }
                        },
                    }
        app.openapi_schema = document
        return document

    app.openapi = schema
