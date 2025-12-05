#!/usr/bin/env python3
"""
Log Archive Tool - Advanced version with filtering and progress bar
"""

import os
import sys
import tarfile
import argparse
import datetime
import logging
import fnmatch
from pathlib import Path
import shutil
import platform
from tqdm import tqdm  # برای progress bar
import time

def setup_logging(verbose=False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
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

def should_include_file(file_path, include_pattern, exclude_pattern):
    """Check if file should be included based on patterns"""
    filename = os.path.basename(file_path)
    
    # Check exclude pattern first
    if exclude_pattern:
        exclude_patterns = [p.strip() for p in exclude_pattern.split(',')]
        for pattern in exclude_patterns:
            if pattern and fnmatch.fnmatch(filename, pattern):
                return False
    
    # Check include pattern
    if include_pattern:
        include_patterns = [p.strip() for p in include_pattern.split(',')]
        for pattern in include_patterns:
            if pattern and fnmatch.fnmatch(filename, pattern):
                return True
        return False
    
    return True

def compress_logs(log_directory, archive_name, include_pattern=None, exclude_pattern=None, 
                  remove_after_archive=False, verbose=False):
    """Compress the log directory into a tar.gz file with optional filtering"""
    try:
        # Create archive directory if it doesn't exist
        archive_dir = Path("archived_logs")
        archive_dir.mkdir(exist_ok=True)
        
        archive_path = archive_dir / archive_name
        
        # Normalize paths
        log_dir_str = str(log_directory)
        
        # Get list of files to include
        files_to_archive = []
        total_size = 0
        
        for root, dirs, files in os.walk(log_dir_str):
            for file in files:
                file_path = os.path.join(root, file)
                if should_include_file(file_path, include_pattern, exclude_pattern):
                    files_to_archive.append(file_path)
                    total_size += os.path.getsize(file_path)
        
        if not files_to_archive:
            raise Exception(f"No files found matching pattern '{include_pattern}'")
        
        # Create tar.gz archive with progress bar
        if verbose:
            print(f"\nArchiving {len(files_to_archive)} files ({total_size / (1024*1024):.2f} MB)...")
        
        with tarfile.open(archive_path, "w:gz") as tar:
            if verbose:
                # With progress bar
                with tqdm(total=len(files_to_archive), desc="Creating archive", unit="file") as pbar:
                    for file_path in files_to_archive:
                        arcname = os.path.relpath(file_path, log_dir_str)
                        tar.add(file_path, arcname=arcname)
                        pbar.update(1)
            else:
                # Without progress bar
                for file_path in files_to_archive:
                    arcname = os.path.relpath(file_path, log_dir_str)
                    tar.add(file_path, arcname=arcname)
        
        # Remove original files if requested
        removed_files = []
        if remove_after_archive:
            if verbose:
                print("\nRemoving original files...")
            
            for file_path in files_to_archive:
                try:
                    os.remove(file_path)
                    removed_files.append(file_path)
                except Exception as e:
                    logging.warning(f"Could not remove {file_path}: {e}")
        
        return archive_path, len(files_to_archive), total_size, removed_files
        
    except Exception as e:
        raise Exception(f"Failed to create archive: {str(e)}")

def log_archive_operation(archive_path, log_directory, files_archived, total_size, 
                          removed_files, archive_log_file="archive_log.txt"):
    """Log the archive operation details"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        archive_size = os.path.getsize(archive_path) if os.path.exists(archive_path) else 0
        archive_size_mb = archive_size / (1024 * 1024)  # Convert to MB
        original_size_mb = total_size / (1024 * 1024) if total_size > 0 else 0
        
        if original_size_mb > 0:
            compression_ratio = ((original_size_mb - archive_size_mb) / original_size_mb) * 100
        else:
            compression_ratio = 0
        
        log_entry = (
            f"Timestamp: {timestamp}\n"
            f"Original Directory: {log_directory}\n"
            f"Files Archived: {files_archived}\n"
            f"Original Size: {original_size_mb:.2f} MB\n"
            f"Archive: {archive_path}\n"
            f"Archive Size: {archive_size_mb:.2f} MB\n"
            f"Compression Ratio: {compression_ratio:.1f}%\n"
            f"Files Removed: {len(removed_files)}\n"
            f"{'='*50}\n"
        )
        
        # Write to archive log file
        with open(archive_log_file, "a", encoding='utf-8') as f:
            f.write(log_entry)
        
        return log_entry
    except Exception as e:
        raise Exception(f"Failed to log archive operation: {str(e)}")

def get_directory_size(directory, include_pattern=None, exclude_pattern=None):
    """Calculate total size of directory in bytes with filtering"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if should_include_file(filepath, include_pattern, exclude_pattern):
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
    return total_size

def list_log_files(log_directory, include_pattern=None, exclude_pattern=None):
    """List all log files in the directory with filtering"""
    log_files = []
    for root, dirs, files in os.walk(log_directory):
        for file in files:
            filepath = os.path.join(root, file)
            if should_include_file(filepath, include_pattern, exclude_pattern):
                log_files.append(filepath)
    return log_files

def get_windows_logs_directory():
    """Get Windows logs directory path"""
    system_drive = os.environ.get('SystemDrive', 'C:')
    return os.path.join(system_drive, 'Windows', 'System32', 'winevt', 'Logs')

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Log Archive Tool - Advanced version with filtering options"
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
        help="Increase output verbosity and show progress bar",
        action="store_true"
    )
    parser.add_argument(
        "--windows-logs",
        help="Use default Windows logs directory",
        action="store_true"
    )
    parser.add_argument(
        "--pattern",
        help="Pattern to include files (e.g., '*.log', 'error_*', '*.log,*.txt')",
        default=None
    )
    parser.add_argument(
        "--exclude",
        help="Pattern to exclude files (e.g., 'debug_*', 'temp*', '*.tmp,*.bak')",
        default=None
    )
    parser.add_argument(
        "--remove-after-archive",
        help="Remove original files after successful archiving",
        action="store_true"
    )
    parser.add_argument(
        "--list-only",
        help="Only list files that would be archived (dry run)",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logging(args.verbose)
    
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
        
        # Display pattern info
        if args.pattern:
            logger.info(f"Include pattern: {args.pattern}")
        if args.exclude:
            logger.info(f"Exclude pattern: {args.exclude}")
        if args.remove_after_archive:
            logger.info("Will remove original files after archiving")
        
        # Validate directory
        log_dir = validate_directory(log_directory)
        logger.info(f"Directory validated: {log_dir}")
        
        # Get directory info with filtering
        dir_size = get_directory_size(log_dir, args.pattern, args.exclude)
        dir_size_mb = dir_size / (1024 * 1024)
        log_files = list_log_files(log_dir, args.pattern, args.exclude)
        
        logger.info(f"Directory size (filtered): {dir_size_mb:.2f} MB")
        logger.info(f"Number of log files found (filtered): {len(log_files)}")
        
        # List only mode
        if args.list_only:
            logger.info("=== FILES TO BE ARCHIVED ===")
            for i, log_file in enumerate(log_files[:50], 1):  # Show first 50 files
                size_mb = os.path.getsize(log_file) / (1024 * 1024)
                logger.info(f"{i:3d}. {log_file} ({size_mb:.2f} MB)")
            if len(log_files) > 50:
                logger.info(f"... and {len(log_files) - 50} more files")
            logger.info("=== END LIST ===")
            return
        
        if args.verbose and log_files:
            logger.info("Files to be archived:")
            for log_file in log_files[:10]:  # Show first 10 files
                size_mb = os.path.getsize(log_file) / (1024 * 1024)
                logger.info(f"  - {log_file} ({size_mb:.2f} MB)")
            if len(log_files) > 10:
                logger.info(f"  ... and {len(log_files) - 10} more")
        
        # Create archive name
        archive_name = create_archive_name()
        logger.info(f"Archive name: {archive_name}")
        
        # Set output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Compress logs with filtering
        logger.info("Creating archive...")
        archive_path, files_archived, total_size, removed_files = compress_logs(
            str(log_dir), 
            archive_name, 
            args.pattern, 
            args.exclude,
            args.remove_after_archive,
            args.verbose
        )
        
        logger.info(f"Archive created successfully: {archive_path}")
        logger.info(f"Files archived: {files_archived}")
        
        if args.remove_after_archive:
            logger.info(f"Files removed: {len(removed_files)}")
        
        # Log the operation
        log_entry = log_archive_operation(
            archive_path, 
            str(log_dir), 
            files_archived,
            total_size,
            removed_files,
            args.log_file
        )
        
        # Get archive size
        archive_size = os.path.getsize(archive_path)
        archive_size_mb = archive_size / (1024 * 1024)
        compression_ratio = (1 - (archive_size / dir_size)) * 100 if dir_size > 0 else 0
        
        # Final summary
        if args.verbose:
            print("\n" + "=" * 60)
            print("ARCHIVE COMPLETED SUCCESSFULLY")
            print("=" * 60)
        
        logger.info("=" * 50)
        logger.info("ARCHIVE COMPLETED SUCCESSFULLY")
        logger.info("=" * 50)
        logger.info(f"Original directory: {log_dir}")
        logger.info(f"Original size (filtered): {dir_size_mb:.2f} MB")
        logger.info(f"Files archived: {files_archived}")
        logger.info(f"Archive size: {archive_size_mb:.2f} MB")
        logger.info(f"Compression ratio: {compression_ratio:.1f}%")
        if args.remove_after_archive:
            logger.info(f"Files removed: {len(removed_files)}")
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