#!/usr/bin/env python3
"""
Unit tests for Log Archive Tool
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path to import log_archive
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import log_archive

class TestLogArchive(unittest.TestCase):
    
    def setUp(self):
        """Create temporary directory for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.test_dir) / "test_logs"
        self.log_dir.mkdir()
        
        # Create test log files
        test_files = {
            "app.log": "Application log content",
            "error.log": "Error log content",
            "debug.log": "Debug log content",
            "system.log": "System log content",
            "access.txt": "Access log in text file",
            "temp.tmp": "Temporary file",
            "backup.bak": "Backup file",
        }
        
        for filename, content in test_files.items():
            filepath = self.log_dir / filename
            filepath.write_text(content)
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)
    
    def test_create_archive_name(self):
        """Test archive name generation"""
        name = log_archive.create_archive_name()
        self.assertTrue(name.startswith("logs_archive_"))
        self.assertTrue(name.endswith(".tar.gz"))
        self.assertIn("_", name)  # Should have timestamp
    
    def test_should_include_file(self):
        """Test file filtering logic"""
        test_cases = [
            # (filename, include_pattern, exclude_pattern, expected_result)
            ("app.log", "*.log", None, True),
            ("app.log", "*.log", "*.log", False),
            ("app.log", None, "*.log", False),
            ("app.log", "app*", None, True),
            ("app.log", "test*", None, False),
            ("app.log", "*.log,*.txt", None, True),
            ("access.txt", "*.log,*.txt", None, True),
            ("app.log", "*.log", "debug*,temp*", True),
            ("debug.log", "*.log", "debug*,temp*", False),
            ("temp.tmp", "*.log", "debug*,temp*", False),
        ]
        
        for filename, include_pattern, exclude_pattern, expected in test_cases:
            with self.subTest(filename=filename, include=include_pattern, exclude=exclude_pattern):
                result = log_archive.should_include_file(
                    f"/path/to/{filename}", 
                    include_pattern, 
                    exclude_pattern
                )
                self.assertEqual(result, expected)
    
    def test_list_log_files_with_pattern(self):
        """Test listing files with pattern filtering"""
        files = log_archive.list_log_files(
            str(self.log_dir), 
            include_pattern="*.log",
            exclude_pattern=None
        )
        self.assertEqual(len(files), 4)  # app.log, error.log, debug.log, system.log
        
        files = log_archive.list_log_files(
            str(self.log_dir), 
            include_pattern="*.log",
            exclude_pattern="debug*"
        )
        self.assertEqual(len(files), 3)  # app.log, error.log, system.log (exclude debug.log)
    
    def test_get_directory_size_with_filtering(self):
        """Test directory size calculation with filtering"""
        # Get size of all .log files
        size = log_archive.get_directory_size(
            str(self.log_dir),
            include_pattern="*.log",
            exclude_pattern=None
        )
        self.assertGreater(size, 0)
        
        # Get size with exclude pattern
        size_excluded = log_archive.get_directory_size(
            str(self.log_dir),
            include_pattern="*.log",
            exclude_pattern="debug*"
        )
        self.assertLess(size_excluded, size)
    
    def test_validate_directory(self):
        """Test directory validation"""
        # Valid directory should return Path object
        result = log_archive.validate_directory(str(self.log_dir))
        self.assertIsInstance(result, Path)
        
        # Non-existent directory should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            log_archive.validate_directory("/non/existent/path")
    
    def test_get_windows_logs_directory(self):
        """Test Windows logs directory detection"""
        dir_path = log_archive.get_windows_logs_directory()
        self.assertIsInstance(dir_path, str)
        self.assertIn("Windows", dir_path)
        self.assertIn("Logs", dir_path)

if __name__ == "__main__":
    unittest.main()