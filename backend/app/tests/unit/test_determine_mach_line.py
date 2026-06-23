"""
Test cases for determine_mach_line:

1. Valid machine IDs
   - Verify each machine zone maps to the expected odd/even line.

2. Zone boundaries and middle values
   - Verify lower, middle, and upper values for each 42-machine zone.

3. Invalid machine IDs
   - Verify 0 and negative machine IDs return None.

4. Out-of-range machine IDs
   - Verify machine IDs above the third zone return None.
"""

from app.services.utils import determine_mach_line
from app.tests.mocks.determine_mach_line_mocks import (
    make_non_positive_mach_ids,
    make_out_of_range_mach_ids,
    make_valid_mach_line_cases,
)


def test_determine_mach_line_maps_valid_ids_by_zone_and_parity():
    """
    Valid machine IDs should map by zone and odd/even parity.
    """
    mach_line_cases = make_valid_mach_line_cases()

    actual_lines = [
        determine_mach_line(mach_id)
        for mach_id, _ in mach_line_cases
    ]
    expected_lines = [
        expected_line
        for _, expected_line in mach_line_cases
    ]

    assert actual_lines == expected_lines


def test_determine_mach_line_returns_none_for_non_positive_ids():
    """
    Machine IDs that are 0 or negative are invalid.
    """
    mach_ids = make_non_positive_mach_ids()

    actual_lines = [
        determine_mach_line(mach_id)
        for mach_id in mach_ids
    ]

    assert actual_lines == [None, None, None, None, None]


def test_determine_mach_line_returns_none_for_ids_outside_supported_zones():
    """
    Machine IDs above the third zone are unsupported.
    """
    mach_ids = make_out_of_range_mach_ids()

    actual_lines = [
        determine_mach_line(mach_id)
        for mach_id in mach_ids
    ]

    assert actual_lines == [None, None, None]
