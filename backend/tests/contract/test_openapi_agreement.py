import json
from pathlib import Path
from app.main import create_app
from app.settings import Settings


def test_http_paths_and_operation_ids_match_reviewed_contract():
    expected = json.loads(Path("/workspace/contracts/openapi.json").read_text())
    actual = create_app(Settings()).openapi()

    def operations(schema):
        return {
            (path, method): operation["operationId"]
            for path, item in schema["paths"].items()
            for method, operation in item.items()
            if method in ("get", "post", "delete", "put", "patch")
        }

    assert operations(actual) == operations(expected)
    # Error details remain sanitized by handlers, not FastAPI's input echo.
    assert (
        actual["components"]["schemas"]["TurnRequest"]["additionalProperties"] is False
    )


def test_reviewed_schema_fields_and_literal_values_match():
    expected = json.loads(Path("/workspace/contracts/openapi.json").read_text())
    actual = create_app(Settings()).openapi()

    def literals(value):
        result = set(map(str, value.get("enum", [])))
        if "const" in value:
            result.add(str(value["const"]))
        for key in ("anyOf", "oneOf", "allOf"):
            for child in value.get(key, []):
                result.update(literals(child))
        return result

    for name, planned in expected["components"]["schemas"].items():
        if name == "Citation":
            continue  # FastAPI inlines the discriminated union.
        implemented = actual["components"]["schemas"][name]
        fields = planned.get("properties", {})
        assert set(fields) == set(implemented.get("properties", {})), name
        for field, value in fields.items():
            assert literals(value) == literals(implemented["properties"][field]), (
                name,
                field,
            )


def test_reviewed_nested_constraints_and_authentication_documentation():
    expected = json.loads(Path("/workspace/contracts/openapi.json").read_text())
    actual = create_app(Settings()).openapi()

    def resolved(value, document):
        if "$ref" in value:
            target = document
            for segment in value["$ref"].removeprefix("#/").split("/"):
                target = target[segment]
            return resolved(target, document)
        return value

    def compare(planned, implemented, path):
        planned = resolved(planned, expected)
        implemented = resolved(implemented, actual)
        for key in (
            "minLength",
            "maxLength",
            "minimum",
            "maximum",
            "pattern",
            "format",
            "additionalProperties",
        ):
            if key in planned:
                assert planned[key] == implemented.get(key), (path, key)
        for field, value in planned.get("properties", {}).items():
            compare(value, implemented["properties"][field], path + "." + field)
        if "items" in planned:
            compare(planned["items"], implemented["items"], path + "[]")

    for name, planned in expected["components"]["schemas"].items():
        if name != "Citation":
            compare(planned, actual["components"]["schemas"][name], name)
    assert actual["paths"]["/api/materials"]["post"]["security"] == [
        {"SessionCookie": [], "CsrfToken": []}
    ]
    assert (
        "multipart/form-data"
        in actual["paths"]["/api/materials"]["post"]["requestBody"]["content"]
    )
    for item in actual["paths"].values():
        for operation in item.values():
            if not isinstance(operation, dict) or "responses" not in operation:
                continue
            assert operation["responses"]["422"]["content"]["application/json"][
                "schema"
            ]["$ref"].endswith("ErrorEnvelope")
