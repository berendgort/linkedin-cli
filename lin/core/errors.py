"""Map exceptions to error_type and retryable."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lin.core.exceptions import (
    LinAmbiguousError,
    LinAuthError,
    LinError,
    LinHTTPError,
    LinNotFoundError,
    LinParseError,
    LinRateLimitError,
    LinUnsupportedError,
    LinValidationError,
)

__all__ = ("ErrorClassification", "classify_error")


@dataclass(frozen=True)
class ErrorClassification:
    error_type: str
    retryable: bool
    http_status: int | None = None
    retry_after_s: float | None = None

    def as_fields(self) -> dict[str, Any]:
        fields: dict[str, Any] = {
            "error_type": self.error_type,
            "retryable": self.retryable,
        }
        if self.http_status is not None:
            fields["http_status"] = self.http_status
        if self.retry_after_s is not None:
            fields["retry_after_s"] = self.retry_after_s
        return fields


def classify_error(exc: BaseException) -> ErrorClassification:
    if isinstance(exc, LinAmbiguousError):
        return ErrorClassification("ambiguous", retryable=False)
    if isinstance(exc, LinAuthError):
        return ErrorClassification("auth", retryable=False)
    if isinstance(exc, LinValidationError):
        return ErrorClassification("validation_error", retryable=False)
    if isinstance(exc, LinUnsupportedError):
        return ErrorClassification("unsupported", retryable=False)
    if isinstance(exc, LinNotFoundError):
        return ErrorClassification("not_found", retryable=False)
    if isinstance(exc, LinParseError):
        return ErrorClassification("parse_error", retryable=False)
    if isinstance(exc, LinRateLimitError):
        return ErrorClassification(
            "rate_limited",
            retryable=True,
            http_status=exc.status_code,
            retry_after_s=exc.retry_after_s,
        )
    if isinstance(exc, LinHTTPError):
        status = exc.status_code
        retryable = status is not None and (status == 429 or status >= 500)
        return ErrorClassification("http_error", retryable=retryable, http_status=status)
    if isinstance(exc, LinError):
        return ErrorClassification("error", retryable=False)
    return ErrorClassification("error", retryable=False)
