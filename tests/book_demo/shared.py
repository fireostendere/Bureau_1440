from dataclasses import dataclass

DEFAULT_SLOT_WAIT_MS = 20000
CALENDLY_DOMAIN = "calendly.com"
EVENT_TITLE = "30 Minute Meeting"
CALENDAR_HEADING = "Select a Day"
TIME_HEADING = "Select a Time"


@dataclass(frozen=True)
class BookingCopy:
    """Copy strings used across the Book Demo embed."""

    event_title: str = EVENT_TITLE
    calendar_heading: str = CALENDAR_HEADING
    time_heading: str = TIME_HEADING
