import unittest
import os
import shutil
from datetime import datetime
from file_history_dups.__main__ import parse_filename, compute_checksum


class TestDuplicateRemover(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'test_dir'
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_parse_valid_filename(self):
        filename = 'file (2023_04_15 12_30_45 UTC).txt'
        result = parse_filename(filename)
        self.assertIsNotNone(result)
        self.assertEqual(result['base'], 'file')
        self.assertEqual(result['timestamp'], datetime(2023, 4, 15, 12, 30, 45))
        self.assertEqual(result['ext'], 'txt')

    def test_parse_invalid_filename(self):
        filename = 'file.txt'
        result = parse_filename(filename)
        self.assertIsNone(result)

    def test_parse_invalid_timestamp(self):
        filename = 'file (2023_13_01 25_61_61 UTC).txt'
        result = parse_filename(filename)
        self.assertIsNone(result)

    def test_compute_checksum_same_content(self):
        file1 = os.path.join(self.test_dir, 'file1.txt')
        file2 = os.path.join(self.test_dir, 'file2.txt')
        with open(file1, 'w') as f:
            f.write('content')
        with open(file2, 'w') as f:
            f.write('content')
        checksum1, _ = compute_checksum(file1)
        checksum2, _ = compute_checksum(file2)
        self.assertEqual(checksum1, checksum2)

    def test_compute_checksum_different_content(self):
        file1 = os.path.join(self.test_dir, 'file1.txt')
        file2 = os.path.join(self.test_dir, 'file2.txt')
        with open(file1, 'w') as f:
            f.write('content1')
        with open(file2, 'w') as f:
            f.write('content2')
        checksum1, _ = compute_checksum(file1)
        checksum2, _ = compute_checksum(file2)
        self.assertNotEqual(checksum1, checksum2)

    # More tests for process_directory and main
