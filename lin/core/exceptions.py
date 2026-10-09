"""Shared errors. Importable by http and core."""

from __future__ import annotations

from typing import Any

__all__ = (
    "LinAmbiguousError",
    "LinAuthError",
    "LinError",
    "LinHTTPError",
    "LinNotFoundError",
    "LinParseError",
    "LinRateLimitError",
    "LinUnsupportedError",
    "LinValidationError",
)


class LinError(Exception):
    """Base."""


class LinHTTPError(LinError):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class LinRateLimitError(LinHTTPError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = 429,
        retry_after_s: float | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code)
        self.retry_after_s = retry_after_s


class LinAuthError(LinError):
    """Missing or rejected session."""


class LinParseError(LinError):
    pass


class LinNotFoundError(LinError):
    pass


class LinUnsupportedError(LinError):
    """Wire shape not captured yet."""


class LinValidationError(LinError):
    """Caller input or outreach policy failed. Nothing was sent."""


class LinAmbiguousError(LinError):
    """More than one person matched. Caller must pass a slug."""

    def __init__(self, message: str, *, candidates: list[Any]) -> None:
        super().__init__(message)
        self.candidates = candidates
