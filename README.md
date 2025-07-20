# `viewline-command` (viewline)

## Overview
`viewline` is a command-line tool that takes a filename or stream and displays the specified line in context. It is designed to make it easy to extract and view specific lines from text files or input streams.

## Features
- Display specific lines from a file or standard input.
- Handles both text and binary files gracefully.
- Provides context around the specified line for better understanding.

## Installation for End Users

To install `viewline` as a standalone application, use [pipx](https://pipxproject.github.io/pipx/):

```bash
pipx install git+https://github.com/dcloutman/viewline-command.git
```

This will make the `viewline` command available globally.

## Developer Setup

If you are developing or contributing to `viewline`, clone the repository and install it locally:

```bash
# Clone the repository
git clone https://github.com/dcloutman/viewline-command.git
cd viewline-command

# (Recommended) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with development dependencies
pip install -e .[dev]

# Make your changes to the code

# Run tests to verify your changes
pytest

# Optionally, check code style and linting
ruff check .
```

## Usage
The `viewline` command can be used as follows:

```bash
viewline <filename> <line_number>
```

### Examples
1. Display line 42 from a file:
   ```bash
   viewline example.txt 42
   ```

2. Display line 42 from a file with line numbers:
   ```bash
   viewline -n example.txt 42
   ```

3. Use `viewline` from a stream with line numbers:
   ```bash
   cat example.txt | viewline -n 42
   ```

3. Use `viewline` from a stream with line numbers but using pure ASCII (no terminal colors):
   ```bash
   cat example.txt | viewline --plain -n 42
   ```

## Version
Current version: 0.1.0

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
