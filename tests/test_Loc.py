"""
Testing LoC_tracker functionality for calculating total lines changed in a given repository.
"""

import pathlib

from almanack.LoC_tracker import calculate_loc_changes


def test_calculate_loc_changes(repository_paths: dict[str, pathlib.Path]):
    high_entropy_path = repository_paths["high_entropy"]
    low_entropy_path = repository_paths["low_entropy"]

    calculate_loc_changes(high_entropy_path)
    calculate_loc_changes(low_entropy_path)
