import pytest
import os
from datetime import datetime
from file_history_dups.__main__ import parse_filename, compute_checksum, process_directory


def test_parse_valid_filename():
    filename = 'file (2023_04_15 12_30_45 UTC).txt'
    result = parse_filename(filename)
    assert result is not None
    assert result['base'] == 'file'
    assert result['timestamp'] == datetime(2023, 4, 15, 12, 30, 45)
    assert result['ext'] == 'txt'


def test_parse_invalid_filename():
    assert parse_filename('file.txt') is None


def test_parse_invalid_timestamp():
    filename = 'file (2023_13_01 25_61_61 UTC).txt'
    assert parse_filename(filename) is None


def test_compute_checksum_same_content(tmp_path):
    file1 = tmp_path / 'file1.txt'
    file2 = tmp_path / 'file2.txt'
    file1.write_text('content')
    file2.write_text('content')
    checksum1, _ = compute_checksum(str(file1))
    checksum2, _ = compute_checksum(str(file2))
    assert checksum1 == checksum2


def test_compute_checksum_different_content(tmp_path):
    file1 = tmp_path / 'file1.txt'
    file2 = tmp_path / 'file2.txt'
    file1.write_text('content1')
    file2.write_text('content2')
    checksum1, _ = compute_checksum(str(file1))
    checksum2, _ = compute_checksum(str(file2))
    assert checksum1 != checksum2


def test_grouping_by_size(tmp_path):
    test_files = [
        'file (2023_01_01 00_00_00 UTC).txt',
        'file (2023_01_02 00_00_00 UTC).txt',
    ]
    
    for i, filename in enumerate(test_files):
        path = tmp_path / filename
        path.write_text('x' * (5 + i*5))
    
    deleted, skipped = process_directory(str(tmp_path), test_files)
    assert deleted == 0
    assert skipped == 0
