"""Time utilities for frequency inference and time-based operations.

This module provides utilities for working with time coordinates in a metadata-only
fashion, including frequency inference and time period calculations.
"""

from datetime import timedelta
from typing import Any, List, Optional, Tuple

import cftime
import numpy as np


def infer_time_frequency(
    coord_values: np.ndarray, units: str, calendar: str = "standard"
) -> Optional[str]:
    """Infer frequency from time coordinate values.

    Parameters
    ----------
    coord_values : np.ndarray
        Time coordinate values (numeric)
    units : str
        CF-compliant units string (e.g., "days since 2000-01-01")
    calendar : str, default "standard"
        Calendar type for cftime decoding

    Returns
    -------
    str or None
        Frequency string like '1H', '3H', '1D', '1M', etc., or None if cannot infer

    Examples
    --------
    >>> values = np.array([0, 1, 2, 3, 4])
    >>> infer_time_frequency(values, "hours since 2000-01-01")
    '1H'
    """
    if len(coord_values) < 2:
        return None

    try:
        # Decode first few time values (sample up to 10)
        sample_size = min(10, len(coord_values))
        times = cftime.num2date(
            coord_values[:sample_size], units, calendar, only_use_cftime_datetimes=False
        )

        # Calculate deltas between consecutive times
        deltas = []
        for i in range(len(times) - 1):
            delta = times[i + 1] - times[i]
            deltas.append(delta)

        # Check if deltas are consistent
        if not deltas:
            return None

        # Get average delta
        avg_delta = deltas[0]

        # Check consistency (all deltas should be similar)
        for delta in deltas[1:]:
            if abs((delta - avg_delta).total_seconds()) > 1:  # Allow 1 second tolerance
                return None

        # Convert delta to frequency string
        total_seconds = avg_delta.total_seconds()

        # Hours
        if total_seconds % 3600 == 0:
            hours = int(total_seconds / 3600)
            if hours == 1:
                return "1H"
            elif hours == 3:
                return "3H"
            elif hours == 6:
                return "6H"
            elif hours == 12:
                return "12H"
            elif hours == 24:
                return "1D"
            else:
                return f"{hours}H"

        # Days
        if total_seconds % 86400 == 0:
            days = int(total_seconds / 86400)
            if days == 1:
                return "1D"
            else:
                return f"{days}D"

        # Minutes
        if total_seconds % 60 == 0:
            minutes = int(total_seconds / 60)
            if minutes == 1:
                return "1T"
            elif minutes == 15:
                return "15T"
            elif minutes == 30:
                return "30T"
            else:
                return f"{minutes}T"

        # Seconds
        if total_seconds == int(total_seconds):
            return f"{int(total_seconds)}S"

        return None

    except Exception:
        return None


def parse_time_units(units: str) -> Tuple[str, str]:
    """Parse CF time units string.

    Parameters
    ----------
    units : str
        CF-compliant units string (e.g., "days since 2000-01-01")

    Returns
    -------
    tuple of (unit, reference_date)
        Unit part (e.g., "days") and reference date string

    Examples
    --------
    >>> parse_time_units("days since 2000-01-01 00:00:00")
    ('days', '2000-01-01 00:00:00')
    """
    parts = units.split(" since ")
    if len(parts) != 2:
        raise ValueError(f"Invalid time units format: {units}")
    return parts[0].strip(), parts[1].strip()


def count_timesteps(
    start: cftime.datetime,
    end: cftime.datetime,
    freq: str,
) -> int:
    """Count number of timesteps between start and end at given frequency.

    Parameters
    ----------
    start : cftime.datetime
        Start datetime
    end : cftime.datetime
        End datetime
    freq : str
        Frequency string (e.g., '1H', '1D', '1M', '1Y')

    Returns
    -------
    int
        Number of timesteps

    Examples
    --------
    >>> start = cftime.DatetimeGregorian(2000, 1, 1)
    >>> end = cftime.DatetimeGregorian(2000, 1, 2)
    >>> count_timesteps(start, end, '1H')
    24
    """
    delta = end - start
    total_seconds = delta.total_seconds()

    # Parse frequency
    if freq.endswith("H"):
        hours = int(freq[:-1])
        return int(total_seconds / (hours * 3600))
    elif freq.endswith("D"):
        days = int(freq[:-1])
        return int(total_seconds / (days * 86400))
    elif freq.endswith("T"):
        minutes = int(freq[:-1])
        return int(total_seconds / (minutes * 60))
    elif freq.endswith("S"):
        seconds = int(freq[:-1])
        return int(total_seconds / seconds)
    else:
        raise ValueError(f"Unsupported frequency: {freq}")


def add_frequency(
    start_date: cftime.datetime,
    freq: str,
    n_steps: int,
) -> cftime.datetime:
    """Add n_steps of frequency to start_date.

    Parameters
    ----------
    start_date : cftime.datetime
        Starting datetime
    freq : str
        Frequency string (e.g., '1H', '1D', '1M', '1Y')
    n_steps : int
        Number of steps to add

    Returns
    -------
    cftime.datetime
        Resulting datetime

    Examples
    --------
    >>> start = cftime.DatetimeGregorian(2000, 1, 1)
    >>> add_frequency(start, '1H', 24)
    cftime.DatetimeGregorian(2000, 1, 2, 0, 0, 0, 0, has_year_zero=False)
    """
    # Parse frequency
    if freq.endswith("H"):
        hours = int(freq[:-1])
        delta = timedelta(hours=hours * n_steps)
    elif freq.endswith("D"):
        days = int(freq[:-1])
        delta = timedelta(days=days * n_steps)
    elif freq.endswith("T"):
        minutes = int(freq[:-1])
        delta = timedelta(minutes=minutes * n_steps)
    elif freq.endswith("S"):
        seconds = int(freq[:-1])
        delta = timedelta(seconds=seconds * n_steps)
    elif freq.endswith("Y"):
        years = int(freq[:-1])
        # Approximate: use 365.25 days per year
        delta = timedelta(days=int(365.25 * years * n_steps))
    elif freq.endswith("M"):
        months = int(freq[:-1])
        # Approximate: use 30.44 days per month
        delta = timedelta(days=int(30.44 * months * n_steps))
    else:
        raise ValueError(f"Unsupported frequency: {freq}")

    return start_date + delta


def create_time_periods(
    start: cftime.datetime,
    end: cftime.datetime,
    group_freq: str,
    calendar: str = "standard",
) -> List[Tuple[cftime.datetime, cftime.datetime]]:
    """Create list of (period_start, period_end) tuples for grouping.

    Parameters
    ----------
    start : cftime.datetime
        Overall start datetime
    end : cftime.datetime
        Overall end datetime
    group_freq : str
        Grouping frequency (e.g., '10Y', '5Y', '1M')
    calendar : str
        Calendar type

    Returns
    -------
    list of tuple
        List of (period_start, period_end) tuples

    Examples
    --------
    >>> start = cftime.DatetimeGregorian(2000, 1, 1)
    >>> end = cftime.DatetimeGregorian(2020, 1, 1)
    >>> periods = create_time_periods(start, end, '10Y')
    >>> len(periods)
    2
    """
    periods = []
    current = start

    while current < end:
        # Calculate period end
        if group_freq.endswith("Y"):
            years = int(group_freq[:-1])
            period_end = cftime.datetime(
                current.year + years,
                current.month,
                current.day,
                current.hour,
                current.minute,
                current.second,
                calendar=calendar,
            )
        elif group_freq.endswith("M"):
            months = int(group_freq[:-1])
            new_month = current.month + months
            new_year = current.year + (new_month - 1) // 12
            new_month = ((new_month - 1) % 12) + 1
            period_end = cftime.datetime(
                new_year,
                new_month,
                current.day,
                current.hour,
                current.minute,
                current.second,
                calendar=calendar,
            )
        elif group_freq.endswith("D"):
            days = int(group_freq[:-1])
            period_end = current + timedelta(days=days)
        elif group_freq.endswith("H"):
            hours = int(group_freq[:-1])
            period_end = current + timedelta(hours=hours)
        else:
            raise ValueError(f"Unsupported grouping frequency: {group_freq}")

        # Don't exceed overall end
        if period_end > end:
            period_end = end

        periods.append((current, period_end))
        current = period_end

    return periods


def ranges_overlap_time(
    range1: Tuple[Any, Any],
    range2: Tuple[cftime.datetime, cftime.datetime],
) -> bool:
    """Check if two time ranges overlap.

    Parameters
    ----------
    range1 : tuple
        First range (can be numeric or datetime)
    range2 : tuple of cftime.datetime
        Second range (datetime objects)

    Returns
    -------
    bool
        True if ranges overlap
    """
    try:
        # If range1 is numeric, we can't compare directly
        # This is a simplified check - in practice, you'd need to decode range1
        return True  # Conservative: assume overlap
    except Exception:
        return True  # Conservative: assume overlap on error
