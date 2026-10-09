"""Locked connection notes. Post-accept copy is not included because it is off."""

from __future__ import annotations

__all__ = ("NOTE_LIMIT", "NOTE_V20", "NOTE_V21")

NOTE_V20 = (
    "Hi Dr. X - we're a venture-backed clinical oversight startup, bringing experienced "
    "medical leaders on board as fractional directors, advisors, and early partners. "
    "Yours is the type of profile we're looking for. Open to hearing the details?"
)
NOTE_V21 = (
    "Hi Dr. X - venture-backed clinical oversight startup bringing medical leaders on as "
    "fractional directors, advisors, and early partners. Your profile fits. "
    "Open to hearing the details?"
)
NOTE_LIMIT = {"v2": 300, "v21": 200}
