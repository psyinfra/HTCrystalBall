"""Various non-specific utilities."""

import re

from argparse import ArgumentTypeError

from htcrystalball import LOGGER


def validate_storage_size(storage: str) -> str:
    """Validates whether disk and ram input is formatted correctly."""
    pat = re.compile(r"^[0-9]+([kKmMgGtTpP]i?[bB]?)$")

    if not pat.match(storage):
        LOGGER.error(f'Invalid storage value given: {storage}')
        raise ArgumentTypeError(f'Invalid storage value given: {storage}')

    return storage


def validate_duration(duration: str) -> str:
    """Validates time input for job duration."""
    pat = re.compile(r"^([0-9]+([dDhHmMsS]?))?$")

    if not pat.match(duration):
        LOGGER.error(f'Invalid time value given: {duration}')
        raise ArgumentTypeError(f'Invalid time value given: {duration}')

    return duration


def split_num_str(value: str, default_num: float,
                  default_str: str) -> (float, str):
    """
    Splits a string containing numeric and alphabetic characters.

    Input value, expected to be a string starting with numeric and ending on
    alphabetic characters. These are then split into a [number, unit] pair.
    The default_num and default_str are used if the numeric, alphabetic, or
    both are missing.
    """
    if not value:
        return default_num, default_str

    split = re.split(r'(\d*\.?\d+)', value.replace(' ', ''))
    number = float(split[1])
    unit = default_str if not split[2] else split[2]

    return number, unit


def to_binary_gigabyte(number: float, unit: str) -> float:
    """
    Converts number from its unit to GiB account for base2 and base10 units.
    """
    unit = unit.lower()

    if unit in ("kb", "k", "kib"):
        return number / (10 ** 6)
    if unit in ("mb", "m", "mib"):
        return number / (10 ** 3)
    if unit in ("tb", "t", "tib"):
        return number * (10 ** 3)
    if unit in ("pb", "p", "pib"):
        return number * (10 ** 6)

    return number


def kib_to_gib(size: float) -> float:
    """Convert disk space unit from KiB to GiB."""
    return round(size / 2 ** 20, 2)


def mib_to_gib(size: float) -> float:
    """Convert memory unit from MiB to GiB."""
    return round(size / 2 ** 10, 2)


def to_minutes(number: float, unit: str) -> float:
    """Converts a number from its unit to minutes."""
    unit = unit.lower()
    if unit in ("d", "dd"):
        return number * 24 * 60
    if unit in ("h", "hh"):
        return number * 60
    if unit in ("s", "ss"):
        return number / 60

    return number


def minutes_to_hours(number: float) -> int:
    """Converts minutes to hours and rounds."""
    return int(number / 60.0 + 0.5)


def hours_to_days(number: float) -> int:
    """Converts hours to days and rounds."""
    return int(number / 24.0 + 0.5)


def compare_requested_available(req: float, avail: float) -> str:
    if req <= 0.01:
        return "green"
    elif avail < req:
        return "red"
    elif (req / avail) > 0.95:
        return "yellow"
    else:
        return "green"
