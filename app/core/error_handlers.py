from typing import List
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY

from app.models.errors import ErrorResponse, FieldError


def build_field_errors(exception: RequestValidationError) -> List[FieldError]:
    field_errors: List[FieldError] = []

    for error in exception.errors():
        loc = error.get("loc", [])
        msg = error.get("msg", "Validation error")
        error_type = error.get("type", "validation_error")

        # loc looks like: ('body', 'created_at') or ('body','conversation_message','author','id')
        # Remove leading 'body'
        loc_parts = [str(x) for x in loc if x != "body"]
        field_path = ".".join(loc_parts) if loc_parts else "body"

        # Map error types to simpler issues
        if error_type in ("missing", "value_error.missing"):
            issue = "missing"
        elif "type_error" in error_type:
            issue = "type_error"
        elif error_type == "json_invalid":
            issue = "invalid_json"
        else:
            issue = "invalid"

        field_errors.append(FieldError(field=field_path, issue=issue, message=msg))

    return field_errors


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    # Detect malformed JSON (FastAPI may encode this as a validation error)
    # One common signature: err['type'] == 'json_invalid'
    is_json_invalid = any(e.get("type") == "json_invalid" for e in exc.errors())

    if is_json_invalid:
        body = ErrorResponse(
            error_code="invalid_json",
            message="Malformed JSON body",
            details=None,
        )
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content=body.model_dump())

    # Otherwise: normal 422 validation errors
    details = build_field_errors(exc)
    body = ErrorResponse(
        error_code="validation_error",
        message="Payload validation failed",
        details=details,
    )
    return JSONResponse(status_code=HTTP_422_UNPROCESSABLE_ENTITY, content=body.model_dump())
