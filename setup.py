import os
from setuptools import setup

# خواندن فایل README
current_dir = os.path.dirname(os.path.abspath(__file__))
readme_path = os.path.join(current_dir, "README.md")

if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "A CLI tool to compress and archive log files"

setup(
    name="log-archive-tool-advanced",
    version="2.0.0",
    description="An advanced CLI tool to compress and archive log files with filtering and progress bar",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Erfan",
    author_email="your.email@example.com",
    url="https://github.com/vasei-me/log-archive-tool",
    py_modules=["log_archive"],
    install_requires=[
        "tqdm>=4.65.0",  # برای progress bar
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
        ],
    },
    entry_points={
        'console_scripts': [
            'log-archive=log_archive:main',
            'log-archive-advanced=log_archive:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Topic :: System :: Archiving",
        "Topic :: System :: Logging",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    keywords="log archive compression cli tar gz filtering progress",
    project_urls={
        "Source": "https://github.com/vasei-me/log-archive-tool",
        "Issues": "https://github.com/vasei-me/log-archive-tool/issues",
    },
)