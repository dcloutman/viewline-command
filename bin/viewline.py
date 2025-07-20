#!/usr/bin/env python
import os
import click
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lib import viewline_impl

os.environ["CLICK_FORCE_PROMPT"] = "1"

@click.command()
@click.argument('line', type=int)
@click.argument('file', required=False, type=click.File('r'))
@click.option('-c', '--context', default=5, type=int, help='Number of context lines to show on either side.')
@click.option('--plain', is_flag=True, help='Disable color highlighting, use asterisk for selected line.')
@click.option('-n', is_flag=True, help='Show line numbers on the right.')
@click.option('--no-highlight', is_flag=True, help='Do not highlight the selected line.')
def viewline(line, file, context, plain, n, no_highlight):
    """Display a specific line (with optional context) from a file or stdin."""
    def click_echo(msg):
        click.echo(msg)
    def click_error(msg, echo_func=None):
        click.echo(msg, err=True)
    viewline_impl(line, file, context, plain, n, no_highlight)

def main():
    viewline()

if __name__ == '__main__':
    main()
