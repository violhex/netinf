#!/usr/bin/env python3
"""
generate_report.py

A lightweight static HTML report generator for JSON data.
Uses Tailwind CSS (via CDN) to render a modern, ShadCN-inspired UI without JS.

Usage:
    python src/generate_report.py data.json output.html
"""
import sys
import json
import argparse
from typing import Any, Dict, List, Union
import html

def load_data(path: str) -> Any:
    """Load JSON data from a file path."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_html(data: Union[Dict[str, Any], List[Dict[str, Any]]],
                  title: str = "Data Report") -> str:
    """Generate HTML report from a mapping or sequence of mappings."""
    # HTML escape helper
    escape = html.escape
    # Network report styling: cards and collapsible sections
    if isinstance(data, dict) and 'interfaces' in data and 'io_counters' in data:
        # Host info cards
        host_cards = ""
        for key, label in [('hostname', 'Hostname'), ('fqdn', 'FQDN'), ('external_ip', 'External IP')]:
            val = data.get(key)
            if val is not None:
                host_cards += (
                    '  <div class="bg-white shadow rounded-lg p-4">'
                    f'<h3 class="text-sm font-medium text-gray-500 uppercase">{escape(label)}</h3>'
                    f'<p class="mt-1 text-lg font-semibold">{escape(val)}</p>'
                    '</div>'
                )

        # Interfaces section
        iface_section = ""
        for iface, addrs in data['interfaces'].items():
            iface_section += (
                '  <details class="mb-4 bg-white shadow rounded-lg">'
                f'<summary class="px-4 py-2 cursor-pointer font-semibold">{escape(iface)}</summary>'
                '<div class="p-4 space-y-2">'
            )
            for addr in addrs:
                fam = addr.get('family', '')
                address = addr.get('address', '')
                netmask = addr.get('netmask')
                broadcast = addr.get('broadcast')
                line = (
                    '<div><span class="font-medium">'
                    f'{escape(fam)}:</span> {escape(address)}'
                )
                if netmask:
                    line += f'<span class="text-xs text-gray-500">/{escape(netmask)}</span>'
                if broadcast:
                    line += f' (broadcast <span class="font-medium">{escape(broadcast)}</span>)'
                line += '</div>'
                iface_section += line
            iface_section += '''
          </div>
        </details>'''

        # I/O counters cards
        io_cards = ""
        for iface, counters in data['io_counters'].items():
            io_cards += (
                '  <div class="bg-white shadow rounded-lg p-4">'
                f'<h3 class="text-sm font-medium text-gray-500 uppercase">{escape(iface)}</h3>'
            )
            for field, label in [('bytes_sent', 'Bytes Sent'), ('bytes_recv', 'Bytes Received'),
                                  ('packets_sent', 'Packets Sent'), ('packets_recv', 'Packets Received')]:
                val = counters.get(field, 0)
                val_str = str(val)
                io_cards += (
                    f'<div class="flex justify-between">'
                    f'<span class="text-sm text-gray-500">{escape(label)}</span>'
                    f'<span class="font-mono">{escape(val_str)}</span>'
                    '</div>'
                )
            io_cards += '</div>'

        # Assemble full HTML
        # Network report HTML with gradient background
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{escape(title)}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body class="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-700 text-gray-900">
  <div class="container mx-auto p-4 space-y-8">
    <h1 class="text-4xl font-extrabold">{escape(title)}</h1>
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
{host_cards}
    </div>
    <section>
      <h2 class="text-xl font-semibold mb-2">Network Interfaces</h2>
{iface_section}
    </section>
    <section>
      <h2 class="text-xl font-semibold mb-2">Network I/O Counters</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
{io_cards}
      </div>
    </section>
  </div>
</body>
</html>"""
    # Generic mapping table for dict
    if isinstance(data, dict):
        header_cells = (
            '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Key</th>'
            '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>'
        )
        rows_html = ""
        for key, val in data.items():
            key_str = escape(str(key))
            if isinstance(val, (dict, list)):
                val_str = escape(json.dumps(val, indent=2))
            else:
                val_str = escape(str(val))
            rows_html += (
                f'<tr class="bg-white">'
                f'<td class="px-6 py-4 whitespace-nowrap">{key_str}</td>'
                f'<td class="px-6 py-4 whitespace-pre-wrap"><pre>{val_str}</pre></td>'
                '</tr>\n'
            )
        columns_html = f'<tr>{header_cells}</tr>'
        table_body = rows_html
    # List of dicts: classic table
    elif isinstance(data, list):
        if not data:
            raise ValueError("No data provided for report generation.")
        columns = list(data[0].keys())
        header_cells = "".join(
            f'<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{escape(str(col))}</th>'
            for col in columns
        )
        rows_html = ""
        for item in data:
            cell_list = []
            for col in columns:
                cell_val = item.get(col, "")
                cell_str = escape(str(cell_val))
                cell_list.append(f'<td class="px-6 py-4 whitespace-nowrap">{cell_str}</td>')
            cells = "".join(cell_list)
            rows_html += f'<tr class="bg-white">{cells}</tr>\n'
        columns_html = f'<tr>{header_cells}</tr>'
        table_body = rows_html
    else:
        raise ValueError(f"Unsupported data type for HTML generation: {type(data)}")

    # Default generic report template with gradient background
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{escape(title)}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body class="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-700 text-gray-900">
  <div class="container mx-auto p-4">
    <h1 class="text-4xl font-extrabold mb-4">{escape(title)}</h1>
    <div class="overflow-x-auto bg-white shadow rounded-lg">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-100">
          {columns_html}
        </thead>
        <tbody class="divide-y divide-gray-200">
          {table_body}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>"""

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a static HTML report from JSON data"
    )
    parser.add_argument(
        'data', metavar='DATA',
        help="Input JSON file ('-' for stdin)"
    )
    parser.add_argument(
        'output', metavar='OUTPUT',
        help="Output HTML file ('-' for stdout)"
    )
    parser.add_argument(
        '--title', '-t', default='Data Report',
        help="Title to display in the report"
    )
    args = parser.parse_args()

    try:
        data = json.load(sys.stdin) if args.data == '-' else load_data(args.data)
    except Exception as e:
        print(f"Error loading JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        html = generate_html(data, title=args.title)
    except Exception as e:
        print(f"Error generating HTML: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.output == '-':
            sys.stdout.write(html)
        else:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"Report generated: {args.output}", file=sys.stderr)
    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()