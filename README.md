# Log Archive Tool

A powerful command-line tool for compressing and archiving log files with automatic timestamping. Perfect for system administrators and developers who need to manage log files efficiently.

## 🚀 Features

- **📦 Smart Compression**: Automatically archives log directories into tar.gz format
- **⏰ Timestamped Archives**: Each archive includes creation timestamp (YYYYMMDD_HHMMSS)
- **📝 Operation Logging**: Logs all archive operations to a file for tracking
- **🖥️ Cross-Platform**: Works on Windows, Linux, and macOS
- **🔧 Zero Dependencies**: Uses only Python standard library
- **🎯 Customizable**: Choose output directory, log file location, and verbosity
- **🔍 File Discovery**: Automatically detects log files by extension or name pattern

## 📦 Installation

### Method 1: Install from source (recommended)

```bash
# Clone the repository
git clone https://github.com/vasei-me/log-archive-tool.git
cd log-archive-tool

# Install in development mode
pip install -e .
```

### Method 2: Direct usage (no installation needed)

```bash
python log_archive.py --help
```

### Method 3: Using pip

```bash
pip install git+https://github.com/vasei-me/log-archive-tool.git
```

## 🎯 Quick Start

1. **Archive a directory:**

```bash
log-archive ./my_logs
```

2. **Archive with detailed output:**

```bash
log-archive ./my_logs -v
```

3. **Archive with custom settings:**

```bash
log-archive ./my_logs -o ./backups -l archive_history.txt
```

## 📖 Usage

### Basic Command Syntax

```bash
log-archive [log_directory] [options]
```

### Options

| Option                                   | Description                                                          | Default           |
| ---------------------------------------- | -------------------------------------------------------------------- | ----------------- |
| `log_directory`                          | Path to the log directory to archive                                 | Current directory |
| `-h, --help`                             | Show help message and exit                                           | -                 |
| `-v, --verbose`                          | Enable verbose output with detailed information                      | False             |
| `-o OUTPUT_DIR, --output-dir OUTPUT_DIR` | Custom output directory for archives                                 | `./archived_logs` |
| `-l LOG_FILE, --log-file LOG_FILE`       | Custom operation log file                                            | `archive_log.txt` |
| `--windows-logs`                         | Use default Windows logs directory (C:\Windows\System32\winevt\Logs) | False             |

### Examples

**Example 1: Archive application logs**

```bash
log-archive /var/log/myapp -v
```

**Example 2: Archive with custom output location**

```bash
log-archive /opt/logs -o /mnt/backups/log_archives
```

**Example 3: Archive Windows Event Logs**

```bash
log-archive --windows-logs -v
```

**Example 4: Archive and track operations**

```bash
log-archive ./logs -l monthly_archive.log -o ./monthly_backups
```

**Example 5: Get help**

```bash
log-archive --help
```

## 📁 Archive Structure

### Archive Naming Pattern

Archives follow this naming convention:

```
logs_archive_YYYYMMDD_HHMMSS.tar.gz
```

Example: `logs_archive_20251205_184052.tar.gz`

### Output Files

The tool creates:

1. **Archive file**: `archived_logs/logs_archive_*.tar.gz`
2. **Operation log**: `archive_log.txt` (customizable with `-l` option)
3. **Tool log**: `log_archive_tool.log` (for debugging)

### Operation Log Format

```
Timestamp: 2025-12-05 18:40:52
Original Directory: /path/to/logs
Archive: archived_logs/logs_archive_20251205_184052.tar.gz
Archive Size: 45.67 MB
==================================================
```

## 🛠️ How It Works

1. **Directory Validation**: Checks if the specified directory exists and is accessible
2. **Log File Discovery**: Scans for files with `.log` extension or containing "log" in filename
3. **Archive Creation**: Creates timestamped tar.gz archive preserving directory structure
4. **Logging**: Records operation details including timestamp, source, and archive size
5. **Summary Display**: Shows compression statistics and operation results

## 🌍 Platform Support

### Windows

```bash
# Archive Windows logs (run as Administrator)
log-archive --windows-logs -v

# Archive custom directory
log-archive "C:\Program Files\MyApp\logs" -o "D:\Backups"
```

### Linux/Mac

```bash
# Archive system logs (may need sudo)
sudo log-archive /var/log -v

# Archive user logs
log-archive ~/app/logs -o ~/backups
```

## 📊 Real-World Use Cases

### Daily Log Rotation

```bash
# Add to crontab (Linux) or Task Scheduler (Windows)
log-archive /var/log/myapp -o /backups/daily -l daily_rotation.log
```

### Pre-Cleanup Archiving

```bash
# Archive logs before cleanup to save space
log-archive /opt/logs -v -l pre_cleanup.log
```

### Monthly Archive Management

```bash
# Archive and compress monthly logs
log-archive /var/log/apache2 -o /archive/monthly -l monthly_archive_$(date +%Y%m).log
```

## 🔧 Development

### Prerequisites

- Python 3.6 or higher
- Git (for cloning)

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/vasei-me/log-archive-tool.git
cd log-archive-tool

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Create test logs
mkdir -p test_logs
echo "Test log entry" > test_logs/app.log
echo "Error log" > test_logs/error.log

# Run the tool
log-archive test_logs -v

# Verify output
ls -la archived_logs/
cat archive_log.txt
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: Permission denied error

```bash
# Solution: Run with appropriate permissions
sudo log-archive /var/log  # Linux/Mac
# Or run PowerShell/CMD as Administrator on Windows
```

**Issue**: "No log files found"

```bash
# Solution: The tool looks for *.log files or files with "log" in name
# Use verbose mode to see what files are detected:
log-archive ./my_directory -v
```

**Issue**: Negative compression ratio

```
# Explanation: This is normal for small files due to tar.gz overhead
# For larger log files (MB+), you'll see positive compression
```

**Issue**: Git authentication errors

```bash
# Solution: Use GitHub Personal Access Token instead of password
# Generate at: https://github.com/settings/tokens
```

### Verbose Mode Output

```bash
log-archive ./logs -v
# Shows:
# - Operating system detection
# - Directory size calculation
# - Log file discovery list
# - Archive creation progress
# - Compression statistics
```

## 📈 Performance

- **Memory Efficient**: Processes files without loading entire contents into memory
- **Fast Compression**: Uses Python's built-in tarfile and gzip modules
- **Scalable**: Handles directories with thousands of log files
- **Resource Friendly**: Minimal CPU and memory usage

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report Bugs**: Open an issue with detailed description
2. **Request Features**: Suggest new functionality
3. **Submit Code**: Fork the repo and create a pull request

### Contribution Guidelines

- Follow PEP 8 style guide for Python code
- Add tests for new functionality
- Update documentation accordingly
- Keep commits focused and descriptive

### Development Workflow

```bash
# 1. Fork the repository
# 2. Clone your fork
git clone https://github.com/your-username/log-archive-tool.git

# 3. Create a feature branch
git checkout -b feature/new-feature

# 4. Make changes and commit
git commit -m "Add new feature description"

# 5. Push to your fork
git push origin feature/new-feature

# 6. Create Pull Request on GitHub
```
