# `lineview` Command

## Overview
`lineview` is a command-line tool that takes a filename or stream and displays the specified line in context. It is designed to make it easy to extract and view specific lines from text files or input streams.

## Features
- Display specific lines from a file or standard input.
- Handles both text and binary files gracefully.
- Provides context around the specified line for better understanding.

## Installation
To install `lineview`, clone this repository and ensure you have Python installed on your system. Then, run:

```bash
pip install .
```

## Usage
The `lineview` command can be used as follows:

```bash
lineview <filename> <line_number>
```

### Examples
1. Display line 42 from a file:
   ```bash
   lineview example.txt 42
   ```

2. Display line 42 from a file with line numbers:
   ```bash
   lineview -n example.txt 42
   ```

3. Use `lineview` from a stream with line numbers:
   ```bash
   cat example.txt | lineview -n 42
   ```

3. Use `lineview` from a stream with line numbers but using pure ASCII (no terminal colors):
   ```bash
   cat example.txt | lineview --plain -n 42
   ```

## Version
Current version: 0.0.1

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
