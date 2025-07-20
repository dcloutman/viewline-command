import sys
import click
import shutil
import os
import io
from typing import NoReturn, TextIO, Any

def is_file_binary(file_obj) -> bool:
    """Return True if the file-like object contains null bytes in the first 1024 bytes."""
    try:
        # Try to read a sample and rewind if possible
        if hasattr(file_obj, 'tell') and hasattr(file_obj, 'seek') and file_obj.seekable():
            original_file_position = file_obj.tell()
            sample = file_obj.read(1024)
            file_obj.seek(original_file_position)
        else:
            sample = file_obj.read(1024)
            # Can't rewind, so leave as is
        if isinstance(sample, str):
            sample = sample.encode('utf-8', errors='replace')
        return b'\x00' in sample
    except Exception:
        return False


def _write_error(msg) -> None:
    """Write an error message to stderr."""
    print(msg, sys.stderr)

def _write_error_and_exit (msg, code=1) -> NoReturn:
    """Write an error message to stderr and exit with the given code."""
    _write_error(msg)
    exit(code)

def _default_exit_func(code=1) -> NoReturn:
    exit(code)

def lineview_impl(line, file, context, plain, n, no_highlight) -> NoReturn:
    """Implementation for displaying a specific line (with optional context) from a file or stdin."""
    # Check that the selected line and context are poisitive integers.
    if not isinstance(line, int) or line < 1:
        _write_error_and_exit('Error: Selected line must be a positive integer.')
    if not isinstance(context, int) or context < 0:
        _write_error_and_exit('Error: Context must be a non-negative integer.')
    
    if file is None:
        input_stream: TextIO = sys.stdin # Start streaming. A test for binary follows below. 
    else:
        # If `file` is a string, treat it as a file path.
        if isinstance(file, str):
            #Check for the existence of the file specified by the string.
            if not os.path.exists(file):
                _write_error_and_exit(f"Error: File '{file}' does not exist.")
            
            # The file path points to an existing file, so check if it's readable.
            if not os.access(file, os.R_OK):
                _write_error_and_exit(f"Error: File '{file}' exists but is not readable.")

            # The file path seems to be valid, so try to open it.
            try:
                input_stream: TextIO = open(file, 'r')
            except Exception as e:
                _write_error_and_exit(f"Error opening file '{file}': {e}")
        
        # Here, we anticipate that a file was passed to this function via Click.
        else:
            # Check if file is a file-like object (has 'read' and '__iter__')
            if not (hasattr(file, 'read') and hasattr(file, '__iter__')):
                _write_error_and_exit('Error: Invalid file input. Please provide a valid file path.')
            input_stream: TextIO = file
    try:
        sample = None
        # For file-like objects, try to sample and then rewind
        if hasattr(input_stream, 'buffer'):
            try:
                initial_stream_offset = input_stream.buffer.tell() if hasattr(input_stream.buffer, 'tell') and input_stream.buffer.seekable() else None
                sample = input_stream.buffer.read(1024)
                # Rewind after sampling
                if initial_stream_offset is not None:
                    input_stream.buffer.seek(initial_stream_offset)
                else:
                    # Non-seekable: buffer sample and rest of stream
                    rest = input_stream.buffer.read()
                    full_bytes: bytes = sample + rest
                    # Binary detection before decoding
                    if is_file_binary(file):
                        _write_error_and_exit('Error: Binary input detected. This tool only supports text files and streams.')
                    text = full_bytes.decode('utf-8', errors='replace')
                    input_stream = io.StringIO(text)
            except Exception:
                sample = None
        else:
            try:
                initial_stream_offset = input_stream.tell() if hasattr(input_stream, 'tell') and input_stream.seekable() else None
                if initial_stream_offset is not None:
                    sample = input_stream.read(1024)
                    input_stream.seek(initial_stream_offset)
                else:
                    # Non-seekable: buffer sample and rest of stream
                    sample = input_stream.read(1024)
                    rest = input_stream.read()
                    input_stream = io.StringIO(sample + rest)
            except Exception:
                sample = None
        if sample is not None:
            if isinstance(sample, bytes) and is_file_binary(io.BytesIO(sample)):
                _write_error_and_exit('Error: Binary input detected. This tool only supports text files and streams.')
            elif isinstance(sample, str) and '\x00' in sample:
                _write_error_and_exit('Error: Binary input detected. This tool only supports text files and streams.')
    except Exception as e:
        _write_error_and_exit(f'Error reading input: {e}')
    start: int = max(1, line - context)
    end: int = max(line + context, start)
    current = 0
    width = len(str(end))
    found = False
    lines = []
    for l in input_stream:
        current += 1
        if current < start:
            continue
        if current > end:
            break
        lines.append((current, l))
        if current == line:
            found = True
    if not found:
        _write_error_and_exit(f"Error: Line {line} out of range.")
    for idx, l in lines:
        display = l.rstrip('\n')
        is_selected = idx == line
        if n:
            line_num_str = f"{str(idx).rjust(width)}: "
            if plain:
                if is_selected:
                    if not no_highlight:
                        display = f"* {line_num_str}{display}"
                    else:
                        display = f"  {line_num_str}{display}"
                else:
                    display = f"  {line_num_str}{display}"
            else:
                display = f"{line_num_str}{display}"
        elif plain:
            if is_selected:
                if not no_highlight:
                    display = f"* {display}"
                else:
                    display = f"  {display}"
            else:
                display = f"  {display}"
        if is_selected and not plain and not no_highlight:
            display = f"\033[1;97;45m{display}\033[0m"
        print(display)
    exit(0)
