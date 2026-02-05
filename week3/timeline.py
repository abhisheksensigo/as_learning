"""Parse timeline strings into date ranges for API filters."""

import re
from datetime import date, timedelta


def parse_timeline(timeline: str) -> tuple[str, str] | None:
    """Parse a timeline string into (from_date, to_date) as YYYY-MM-DD.

    Supports:
    - last 1 year, last year, last 2 years
    - last month, last 3 months
    - last week, last 2 weeks
    - in 2024, 2024
    - January 2023, Jan 2023
    - 2024-01, 2023-06

    Returns None if not parseable.
    """
    s = (timeline or "").strip().lower()
    if not s:
        return None

    today = date.today()

    # last N year(s)
    m = re.match(r"last\s+(\d+)\s*year(s)?", s)
    if m:
        n = int(m.group(1))
        from_d = today - timedelta(days=365 * n)
        return (from_d.isoformat(), today.isoformat())

    if re.match(r"last\s+year", s):
        from_d = today - timedelta(days=365)
        return (from_d.isoformat(), today.isoformat())

    # last N month(s)
    m = re.match(r"last\s+(\d+)\s*month(s)?", s)
    if m:
        n = int(m.group(1))
        from_d = today - timedelta(days=30 * n)
        return (from_d.isoformat(), today.isoformat())

    if re.match(r"last\s+month", s):
        from_d = today - timedelta(days=30)
        return (from_d.isoformat(), today.isoformat())

    # last N week(s)
    m = re.match(r"last\s+(\d+)\s*week(s)?", s)
    if m:
        n = int(m.group(1))
        from_d = today - timedelta(weeks=n)
        return (from_d.isoformat(), today.isoformat())

    if re.match(r"last\s+week", s):
        from_d = today - timedelta(weeks=1)
        return (from_d.isoformat(), today.isoformat())

    # in YYYY or YYYY
    m = re.match(r"(?:in\s+)?(\d{4})$", s)
    if m:
        y = int(m.group(1))
        return (f"{y}-01-01", f"{y}-12-31")

    # Month YYYY (January 2023, Jan 2023)
    months = {
        "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
        "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
        "august": 8, "aug": 8, "september": 9, "sep": 9, "october": 10, "oct": 10,
        "november": 11, "nov": 11, "december": 12, "dec": 12,
    }
    m = re.match(r"(\w+)\s+(\d{4})", s)
    if m:
        mon_str, year_str = m.group(1), m.group(2)
        if mon_str in months:
            y, m_num = int(year_str), months[mon_str]
            from_d = date(y, m_num, 1)
            if m_num == 12:
                to_d = date(y, 12, 31)
            else:
                to_d = date(y, m_num + 1, 1) - timedelta(days=1)
            return (from_d.isoformat(), to_d.isoformat())

    # YYYY-MM
    m = re.match(r"(\d{4})-(\d{1,2})$", s)
    if m:
        y, m_num = int(m.group(1)), int(m.group(2))
        if 1 <= m_num <= 12:
            from_d = date(y, m_num, 1)
            if m_num == 12:
                to_d = date(y, 12, 31)
            else:
                to_d = date(y, m_num + 1, 1) - timedelta(days=1)
            return (from_d.isoformat(), to_d.isoformat())

    return None


def timeline_to_minutes(timeline: str) -> int | None:
    """Convert timeline to minutes for GDELT lastminutes.
    Only supports 'last X year/month/week' formats. Returns None for 'in 2024', 'January 2023', etc.
    """
    s = (timeline or "").strip().lower()
    if not s:
        return None

    # last N year(s)
    m = re.match(r"last\s+(\d+)\s*year(s)?", s)
    if m:
        return max(60, int(m.group(1)) * 365 * 24 * 60)
    if re.match(r"last\s+year", s):
        return 365 * 24 * 60

    # last N month(s)
    m = re.match(r"last\s+(\d+)\s*month(s)?", s)
    if m:
        return max(60, int(m.group(1)) * 30 * 24 * 60)
    if re.match(r"last\s+month", s):
        return 30 * 24 * 60

    # last N week(s)
    m = re.match(r"last\s+(\d+)\s*week(s)?", s)
    if m:
        return max(60, int(m.group(1)) * 7 * 24 * 60)
    if re.match(r"last\s+week", s):
        return 7 * 24 * 60

    return None
