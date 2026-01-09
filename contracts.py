from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Iterable, Optional

from flask import request, jsonify
from werkzeug.exceptions import BadRequest


@dataclass(frozen=True)
class ApiError:
    status: int
    message: str
    key: str = "Error" 


def error_response(status: int, message: str, key: str = "Error"):
    return jsonify({key: message}), status


# -------------------------
# Accept / Content-Type
# -------------------------

def require_accept_json(fn: Callable):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print("ACCEPT CHECK v2:", request.headers.get("Accept"))
        accept = request.headers.get("Accept")
        if not accept or accept.strip() == "":
            return fn(*args, **kwargs)

        if request.accept_mimetypes["application/json"] > 0 or request.accept_mimetypes["application/*+json"] > 0:
            return fn(*args, **kwargs)

        return error_response(
            406,
            "Not Acceptable: API supports application/json responses only."
        )
    return wrapper


# if endpoint expects a JSON body, Content-Type must be application/json. If absent/different -> 415.
def require_content_type_json(fn: Callable):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        ct = request.content_type or ""
        if not ct.lower().startswith("application/json"):
            return error_response(415, "Unsupported Media Type: Content-Type must be application/json.")
        return fn(*args, **kwargs)
    return wrapper


# -------------------------
# Body presence rules
# -------------------------

# For endpoints where spec says Request Body: None. If ANY body content is present -> 400
def reject_body(fn: Callable):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # request.get_data reads raw body; if client sends whitespace/newline,
        # spec usually still considers that “content”.
        raw = request.get_data
        if raw and len(raw) > 0:
            return error_response(400, "Bad Request: request body not allowed for this endpoint.")
        return fn(*args, **kwargs)
    return wrapper


# -------------------------
# JSON parsing + field validation
# -------------------------

# Returns parsed JSON dict (or list/primitive) with strict behavior. 400 for invalid/missing
def parse_json_strict(required: bool):
    raw = request.get_data
    if not raw or len(raw) == 0:
        if required:
            raise ApiContractViolation(400, "Bad Request: JSON body required.")
        return None

    try:
        return request.get_json(force=True, silent=False)
    except BadRequest:
        raise ApiContractViolation(400, "Bad Request: invalid JSON.")


class ApiContractViolation(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


# Enforce JSON body required + field rules.
def require_json_body(
    *,
    required_fields: Optional[Iterable[str]] = None,
    at_least_one_of: Optional[Iterable[str]] = None,
):
    required_fields = list(required_fields or [])
    at_least_one_of = list(at_least_one_of or [])

    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                body = parse_json_strict(required=True)
            except ApiContractViolation as e:
                return error_response(e.status, e.message)

            if not isinstance(body, dict):
                return error_response(400, "Bad Request: JSON body must be an object.")

            if required_fields:
                missing = [k for k in required_fields if k not in body]
                if missing:
                    return error_response(400, f"Bad Request: missing required fields: {', '.join(missing)}.")

            if at_least_one_of:
                if not any(k in body for k in at_least_one_of):
                    return error_response(400, f"Bad Request: must include at least one of: {', '.join(at_least_one_of)}.")

            request.parsed_json = body
            return fn(*args, **kwargs)

        return wrapper
    return decorator


def optional_json_body(fn: Callable):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            body = parse_json_strict(required=False)
        except ApiContractViolation as e:
            return error_response(e.status, e.message)

        if body is not None and not isinstance(body, dict):
            return error_response(400, "Bad Request: JSON body must be an object.")

        request.parsed_json = body
        return fn(*args, **kwargs)
    return wrapper
