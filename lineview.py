#!/usr/bin/env python
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


def _default_error_func(msg, echo_func=print):
    echo_func(msg)

def _default_exit_func(code=1) -> NoReturn:
    sys.exit(code)

def lineview_impl(line, file, context, plain, n, no_highlight, echo_func=print, error_func=None, exit_func=None):
    """Implementation for displaying a specific line (with optional context) from a file or stdin."""
    
    if error_func is None:
        error_func = _default_error_func
    if exit_func is None:
        exit_func = _default_exit_func

    # Check that the selected line and context are poisitive integers.
    if not isinstance(line, int) or line < 1:
        error_func('Error: Selected line must be a positive integer.', echo_func)
        exit_func(1)
    if not isinstance(context, int) or context < 0:
        error_func('Error: Context must be a non-negative integer.', echo_func)
        exit_func(1)
    
    if file is None:
        input_stream: TextIO = sys.stdin # Start streaming. A test for binary follows below. 
    else:
        # If `file` is a string, treat it as a file path.
        if isinstance(file, str):
            #Check for the existence of the file specified by the string.
            if not os.path.exists(file):
                error_func(f"Error: File '{file}' does not exist.", echo_func)
                exit_func(1)
            
            # The file path points to an existing file, so check if it's readable.
            if not os.access(file, os.R_OK):
                error_func(f"Error: File '{file}' exists but is not readable.", echo_func)
                exit_func(1)

            # The file path seems to be valid, so try to open it.
            try:
                input_stream: TextIO = open(file, 'r')
            except Exception as e:
                error_func(f"Error opening file '{file}': {e}", echo_func)
                exit_func(1)
        
        # Here, we anticipate that a file was passed to this function via Click.
        else:
            # Check if file is a file-like object (has 'read' and '__iter__')
            if not (hasattr(file, 'read') and hasattr(file, '__iter__')):
                error_func('Error: Invalid file input. Please provide a valid file path.', echo_func)
                exit_func(1)
            input_stream: TextIO = file
    try:
        sample = None
        # For file-like objects, try to sample and then rewind
        if hasattr(input_stream, 'buffer'):
            try:
                input_stream_offset = input_stream.buffer.tell() if hasattr(input_stream.buffer, 'tell') and input_stream.buffer.seekable() else None
                sample = input_stream.buffer.read(1024)
                # Rewind after sampling
                if input_stream_offset is not None:
                    input_stream.buffer.seek(input_stream_offset)
                else:
                    # Non-seekable: buffer sample and rest of stream
                    rest = input_stream.buffer.read()
                    full_bytes: bytes = sample + rest
                    # Binary detection before decoding
                    if is_file_binary(file):
                        error_func('Error: Binary input detected. This tool only supports text files and streams.', echo_func)
                        exit_func(1)
                    text = full_bytes.decode('utf-8', errors='replace')
                    input_stream = io.StringIO(text)
            except Exception:
                sample = None
        else:
            try:
                input_stream_offset = input_stream.tell() if hasattr(input_stream, 'tell') and input_stream.seekable() else None
                if input_stream_offset is not None:
                    sample = input_stream.read(1024)
                    input_stream.seek(input_stream_offset)
                else:
                    # Non-seekable: buffer sample and rest of stream
                    sample = input_stream.read(1024)
                    rest = input_stream.read()
                    input_stream = io.StringIO(sample + rest)
            except Exception:
                sample = None
        if sample is not None:
            if isinstance(sample, bytes) and is_file_binary(io.BytesIO(sample)):
                error_func('Error: Binary input detected. This tool only supports text files and streams.', echo_func)
                exit_func(1)
            elif isinstance(sample, str) and '\x00' in sample:
                error_func('Error: Binary input detected. This tool only supports text files and streams.', echo_func)
                exit_func(1)
    except Exception as e:
        error_func(f'Error reading input: {e}', echo_func)
        exit_func(1)
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
        error_func(f"Error: Line {line} out of range.", echo_func)
        exit_func(1)
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
        echo_func(display)

os.environ["CLICK_FORCE_PROMPT"] = "1"

@click.command()
@click.argument('line', type=int)
@click.argument('file', required=False, type=click.File('r'))
@click.option('-c', '--context', default=5, type=int, help='Number of context lines to show on either side.')
@click.option('--plain', is_flag=True, help='Disable color highlighting, use asterisk for selected line.')
@click.option('-n', is_flag=True, help='Show line numbers on the right.')
@click.option('--no-highlight', is_flag=True, help='Do not highlight the selected line.')
def lineview(line, file, context, plain, n, no_highlight):
    """Display a specific line (with optional context) from a file or stdin."""
    def click_echo(msg):
        click.echo(msg)
    def click_error(msg, echo_func=None):
        click.echo(msg, err=True)
    lineview_impl(line, file, context, plain, n, no_highlight, echo_func=click_echo, error_func=click_error, exit_func=sys.exit)

if __name__ == '__main__':
    lineview()
