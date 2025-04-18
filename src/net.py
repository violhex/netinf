#!/usr/bin/env python3
"""
network_info.py: Retrieve and display network information using Rich.
"""

import sys
import socket
import argparse
import json
from typing import Any, Dict, List, Optional, Tuple

try:
    import psutil
except ImportError:
    print("Error: psutil library is required. Install with: pip install psutil")
    sys.exit(1)

try:
    import requests
except ImportError:
    requests = None
    
try:
    import yaml
except ImportError:
    yaml = None
    
try:
    import toml
except ImportError:
    toml = None
# Optional HTML report support via generate_report.py
try:
    import generate_report
except ImportError:
    generate_report = None

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
except ImportError:
    print("Error: rich library is required. Install with: pip install rich")
    sys.exit(1)

def get_hostname_info():
    """Return local hostname and fully qualified domain name."""
    hostname = socket.gethostname()
    fqdn = socket.getfqdn()
    return hostname, fqdn

def get_external_ip():
    """Return external/public IP address if requests is available."""
    if not requests:
        return None
    try:
        resp = requests.get("https://api.ipify.org?format=json", timeout=5)
        resp.raise_for_status()
        return resp.json().get("ip")
    except Exception:
        return None

def get_interfaces():
    """Return network interfaces and their addresses."""
    return psutil.net_if_addrs()

def get_io_counters():
    """Return network I/O statistics per interface."""
    return psutil.net_io_counters(pernic=True)
    
def parse_args():
    parser = argparse.ArgumentParser(description="Network information CLI")
    parser.add_argument(
        '--report-format', '-rf',
        choices=['json', 'yaml', 'toml', 'html'],
        default='json',
        help='Structured report format (json, yaml, toml, or html)'
    )
    parser.add_argument('--gen-report', '-gr', action='store_true',
                        help='Generate structured report instead of console output')
    parser.add_argument('--output', '-o', metavar='FILE',
                        help='Write output to FILE instead of stdout')
    return parser.parse_args()

def get_data():
    hostname, fqdn = get_hostname_info()
    external_ip = get_external_ip()
    interfaces = get_interfaces()
    io_counters = get_io_counters()
    iface_data = {}
    for iface, addrs in interfaces.items():
        entries = []
        for addr in addrs:
            if addr.family == socket.AF_INET:
                fam = 'IPv4'
            elif addr.family == socket.AF_INET6:
                fam = 'IPv6'
            else:
                fam = 'MAC'
            entry = {
                'family': fam,
                'address': addr.address,
                'netmask': addr.netmask,
            }
            if getattr(addr, 'broadcast', None):
                entry['broadcast'] = addr.broadcast
            entries.append(entry)
        iface_data[iface] = entries
    io_data = {}
    for iface, counters in io_counters.items():
        io_data[iface] = {
            'bytes_sent': counters.bytes_sent,
            'bytes_recv': counters.bytes_recv,
            'packets_sent': counters.packets_sent,
            'packets_recv': counters.packets_recv,
        }
    return {
        'hostname': hostname,
        'fqdn': fqdn,
        'external_ip': external_ip,
        'interfaces': iface_data,
        'io_counters': io_data,
    }

def bytes2human(n):
    """Convert bytes to human-readable format."""
    symbols = ("B", "KiB", "MiB", "GiB", "TiB", "PiB")
    prefix = {symbol: 1 << (i * 10) for i, symbol in enumerate(symbols)}
    for symbol in reversed(symbols):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return f"{value:.2f}{symbol}"
    return f"{n}B"

def main():
    args = parse_args()
    if args.gen_report:
        console = Console(stderr=True)
        # Gather data with spinner
        with console.status("[bold green]Gathering network data...", spinner="dots"):
            data = get_data()
        # Generate report
        with console.status("[bold green]Generating report...", spinner="dots"):
            if args.report_format == 'json':
                text = json.dumps(data, indent=2)
            elif args.report_format == 'yaml':
                if not yaml:
                    console.print('Error: PyYAML required for YAML output', style="bold red", file=sys.stderr)
                    sys.exit(1)
                text = yaml.safe_dump(data)
            elif args.report_format == 'toml':
                if not toml:
                    console.print('Error: toml library required for TOML output', style="bold red", file=sys.stderr)
                    sys.exit(1)
                text = toml.dumps(data)
            elif args.report_format == 'html':
                if not generate_report:
                    console.print('Error: generate_report module required for HTML output', style="bold red", file=sys.stderr)
                    sys.exit(1)
                text = generate_report.generate_html(data, title='Network Report')
        # Output report
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as out_f:
                out_f.write(text)
            console.log(f"Report written to [bold]{args.output}[/]")
        else:
            print(text)
        return
    console = Console()
    # Interactive mode: gather data with spinner
    with console.status("[bold green]Gathering network data...", spinner="dots"):
        data = get_data()
    hostname = data.get('hostname')
    fqdn = data.get('fqdn')
    external_ip = data.get('external_ip')
    interfaces = data.get('interfaces', {})
    io_counters = data.get('io_counters', {})

    # Summary of host information
    summary = Table.grid(padding=(0, 1))
    summary.add_column(justify="right", style="bold cyan", no_wrap=True)
    summary.add_column(style="magenta")
    summary.add_row("Hostname", hostname)
    summary.add_row("FQDN", fqdn)
    if external_ip:
        summary.add_row("External IP", external_ip)
    console.print(Panel(summary, title="Host Information", expand=False))

    # Network interfaces and addresses
    tree = Tree("Network Interfaces", guide_style="bold bright_blue")
    for iface, entries in interfaces.items():
        branch = tree.add(f"[bold]{iface}[/]")
        for entry in entries:
            fam = entry.get('family', '')
            address = entry.get('address', '')
            netmask = entry.get('netmask')
            broadcast = entry.get('broadcast')
            line = f"{fam}: [cyan]{address}[/]"
            if netmask:
                line += f" [yellow]/{netmask}[/]"
            if broadcast:
                line += f" (broadcast: [cyan]{broadcast}[/])"
            branch.add(line)
    console.print(tree)

    # Network I/O statistics
    io_table = Table(title="Network IO Counters")
    io_table.add_column("Interface", style="bold")
    io_table.add_column("Bytes Sent", justify="right")
    io_table.add_column("Bytes Recv", justify="right")
    io_table.add_column("Packets Sent", justify="right")
    io_table.add_column("Packets Recv", justify="right")
    for iface, counters in io_counters.items():
        # counters may be dict or psutil._common.snetio
        if isinstance(counters, dict):
            sent = counters.get('bytes_sent', 0)
            recv = counters.get('bytes_recv', 0)
            psent = counters.get('packets_sent', 0)
            precv = counters.get('packets_recv', 0)
        else:
            sent = counters.bytes_sent
            recv = counters.bytes_recv
            psent = counters.packets_sent
            precv = counters.packets_recv
        io_table.add_row(
            iface,
            bytes2human(sent),
            bytes2human(recv),
            str(psent),
            str(precv),
        )
    console.print(io_table)

if __name__ == "__main__":
    main()