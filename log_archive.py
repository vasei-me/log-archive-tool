#!/usr/bin/env python3
"""
Log Archive Tool - A CLI tool to compress and archive log files
"""

import os
import sys
import tarfile
import argparse
import datetime
import logging
from pathlib import Path
import shutil
import platform

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('log_archive_tool.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def validate_directory(directory_path):
    """Validate if the directory exists and is accessible"""
    path = Path(directory_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Directory '{directory_path}' does not exist")
    
    if not path.is_dir():
        raise NotADirectoryError(f"'{directory_path}' is not a directory")
    
    # Check read permissions
    try:
        test_file = path / ".permission_test"
        test_file.touch(exist_ok=True)
        test_file.unlink(missing_ok=True)
    except PermissionError:
        raise PermissionError(f"No write permission for directory '{directory_path}'")
    
    return path

def create_archive_name():
    """Generate archive name with timestamp"""
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    return f"logs_archive_{timestamp}.tar.gz"

def compress_logs(log_directory, archive_name):
    """Compress the log directory into a tar.gz file"""
    try:
        # Create archive directory if it doesn't exist
        archive_dir = Path("archived_logs")
        archive_dir.mkdir(exist_ok=True)
        
        archive_path = archive_dir / archive_name
        
        # Normalize paths for Windows
        log_dir_str = str(log_directory)
        
        # Create tar.gz archive
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(log_dir_str, arcname=os.path.basename(log_dir_str))
        
        return archive_path
    except Exception as e:
        raise Exception(f"Failed to create archive: {str(e)}")

def log_archive_operation(archive_path, log_directory, archive_log_file="archive_log.txt"):
    """Log the archive operation details"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        archive_size = os.path.getsize(archive_path) if os.path.exists(archive_path) else 0
        archive_size_mb = archive_size / (1024 * 1024)  # Convert to MB
        
        log_entry = (
            f"Timestamp: {timestamp}\n"
            f"Original Directory: {log_directory}\n"
            f"Archive: {archive_path}\n"
            f"Archive Size: {archive_size_mb:.2f} MB\n"
            f"{'='*50}\n"
        )
        
        # Write to archive log file
        with open(archive_log_file, "a", encoding='utf-8') as f:
            f.write(log_entry)
        
        return log_entry
    except Exception as e:
        raise Exception(f"Failed to log archive operation: {str(e)}")

def get_directory_size(directory):
    """Calculate total size of directory in bytes"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
    return total_size

def list_log_files(log_directory):
    """List all log files in the directory"""
    log_files = []
    for root, dirs, files in os.walk(log_directory):
        for file in files:
            if file.endswith('.log') or 'log' in file.lower():
                log_files.append(os.path.join(root, file))
    return log_files

def get_windows_logs_directory():
    """Get Windows logs directory path"""
    system_drive = os.environ.get('SystemDrive', 'C:')
    return os.path.join(system_drive, 'Windows', 'System32', 'winevt', 'Logs')

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Log Archive Tool - Compress and archive log files"
    )
    parser.add_argument(
        "log_directory",
        nargs='?',  # Make it optional
        help="Path to the log directory to archive (e.g., C:\\Windows\\Logs)",
        default=None
    )
    parser.add_argument(
        "-o", "--output-dir",
        help="Custom output directory for archives (default: ./archived_logs)",
        default="./archived_logs"
    )
    parser.add_argument(
        "-l", "--log-file",
        help="Custom log file for archive operations (default: archive_log.txt)",
        default="archive_log.txt"
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Increase output verbosity",
        action="store_true"
    )
    parser.add_argument(
        "--windows-logs",
        help="Use default Windows logs directory",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logging()
    
    # Determine log directory
    if args.windows_logs:
        log_directory = get_windows_logs_directory()
        logger.info(f"Using Windows logs directory: {log_directory}")
    elif args.log_directory:
        log_directory = args.log_directory
    else:
        parser.print_help()
        logger.error("No log directory specified. Use --windows-logs for Windows logs or specify a directory.")
        sys.exit(1)
    
    try:
        logger.info(f"Starting log archive process for: {log_directory}")
        logger.info(f"Operating System: {platform.system()} {platform.release()}")
        
        # Validate directory
        log_dir = validate_directory(log_directory)
        logger.info(f"Directory validated: {log_dir}")
        
        # Get directory info
        dir_size = get_directory_size(log_dir)
        dir_size_mb = dir_size / (1024 * 1024)
        log_files = list_log_files(log_dir)
        
        logger.info(f"Directory size: {dir_size_mb:.2f} MB")
        logger.info(f"Number of log files found: {len(log_files)}")
        
        if args.verbose and log_files:
            logger.info("Log files found:")
            for log_file in log_files[:10]:  # Show first 10 files
                logger.info(f"  - {log_file}")
            if len(log_files) > 10:
                logger.info(f"  ... and {len(log_files) - 10} more")
        
        # Create archive name
        archive_name = create_archive_name()
        logger.info(f"Archive name: {archive_name}")
        
        # Set output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Compress logs
        logger.info("Creating archive...")
        archive_path = compress_logs(str(log_dir), archive_name)
        logger.info(f"Archive created successfully: {archive_path}")
        
        # Log the operation
        log_entry = log_archive_operation(
            archive_path, 
            str(log_dir), 
            args.log_file
        )
        
        # Get archive size
        archive_size = os.path.getsize(archive_path)
        archive_size_mb = archive_size / (1024 * 1024)
        compression_ratio = (1 - (archive_size / dir_size)) * 100 if dir_size > 0 else 0
        
        # Final summary
        logger.info("=" * 50)
        logger.info("ARCHIVE COMPLETED SUCCESSFULLY")
        logger.info("=" * 50)
        logger.info(f"Original directory: {log_dir}")
        logger.info(f"Original size: {dir_size_mb:.2f} MB")
        logger.info(f"Archive size: {archive_size_mb:.2f} MB")
        logger.info(f"Compression ratio: {compression_ratio:.1f}%")
        logger.info(f"Archive saved to: {archive_path}")
        logger.info(f"Operation logged to: {args.log_file}")
        logger.info("=" * 50)
        
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    except PermissionError as e:
        logger.error(str(e))
        logger.error("Try running as Administrator if necessary")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()