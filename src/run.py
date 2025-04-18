#!/usr/bin/env python3
"""
run.py: Entry point for Network Info tool

Usage:
    python run.py dev                # Interactive network viewer
    python run.py report [options]   # Generate structured report

Options for report:
    -rf, --report-format <fmt>      Report format: json, yaml, toml, html (default: html)
    -o, --output <file>             Output file path (default: report.html)
"""
import sys
import os

# Ensure src directory is on the import path
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import net

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    # Interactive mode
    if cmd == 'dev':
        sys.argv = ['net'] + sys.argv[2:]
        net.main()
    # Structured report generation
    elif cmd in ('report', 'gen'):
        fmt = 'html'
        out = 'report.html'
        # Parse options
        i = 2
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg in ('-rf', '--report-format') and i + 1 < len(sys.argv):
                fmt = sys.argv[i+1]
                i += 2
                continue
            if arg in ('-o', '--output') and i + 1 < len(sys.argv):
                out = sys.argv[i+1]
                i += 2
                continue
            i += 1
        # Delegate to net.main with proper flags
        sys.argv = ['net', '--gen-report', '--report-format', fmt, '--output', out]
        net.main()
    else:
        print(f"Unknown command '{cmd}'. Valid commands are: dev, report.", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()