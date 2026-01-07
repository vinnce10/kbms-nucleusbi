from typing import List
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY

from app.models.errors import ErrorResponse, FieldError


def build_field_errors(exception: RequestValidationError) -> List[FieldError]:
    """Convert FastAPI/Pydantic validation errors into our stable FieldError schema.

    This keeps error responses consistent for internal consumers and UAT,
    even if Pydantic error formatting changes over time.
    """
    field_errors: List[FieldError] = []

    for error in exception.errors():
        loc = error.get("loc", [])
        msg = error.get("msg", "Validation error")
        error_type = error.get("type", "validation_error")

        # `loc` describes where the error happened, e.g.
        # - ('body', 'created_at')
        # - ('body', 'conversation_message', 'author', 'id')
        # - ('path', 'conversation_id')
        # We remove the leading 'body' so the path matches the JSON payload shape.
        loc_parts = [str(x) for x in loc if x != "body"]
        field_path = ".".join(loc_parts) if loc_parts else "body"

        # Reduce many Pydantic error types into a small, predictable set
        # that clients/tests can reliably assert on.
        if error_type in ("missing", "value_error.missing"):
            issue = "missing"
        elif "type_error" in error_type:
            issue = "type_error"
        elif error_type == "json_invalid":
            issue = "invalid_json"
        else:
            issue = "invalid"

        # Always include a FieldError item so "details" is consistently structured.
        field_errors.append(FieldError(field=field_path, issue=issue, message=msg))

    return field_errors


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """Global handler for request validation.

    - 400 when the request body is not valid JSON (malformed JSON)
    - 422 when JSON is valid but fails schema/type validation
    """
    # FastAPI represents malformed JSON as a validation error with type "json_invalid".
    is_json_invalid = any(e.get("type") == "json_invalid" for e in exc.errors())

    if is_json_invalid:
        body = ErrorResponse(
            error_code="invalid_json",
            message="Malformed JSON body",
            details=None,
        )
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content=body.model_dump())

    # Standard validation errors: missing required fields, wrong types, invalid formats, etc.
    details = build_field_errors(exc)
    body = ErrorResponse(
        error_code="validation_error",
        message="Payload validation failed",
        details=details,
    )
    return JSONResponse(status_code=HTTP_422_UNPROCESSABLE_ENTITY, content=body.model_dump())
