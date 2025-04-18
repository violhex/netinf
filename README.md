# Network Info Tool

This project provides a simple yet powerful CLI and static‑HTML reporting tool for viewing your system’s network interfaces and I/O statistics.

## Usage

### Interactive Mode
Launch the Rich‑powered terminal UI:
```bash
python run.py dev
```

### Generate Structured Report
Produce a JSON/YAML/TOML/HTML report:
```bash
python run.py report -rf html -o report.html
```
Available formats: `json`, `yaml`, `toml`, `html` (default: `html`).

## Packaging as Executable
You can bundle the tool into a single Windows `.exe` using [PyInstaller](https://www.pyinstaller.org/):

1. Install PyInstaller in your virtual environment:
   ```bash
   pip install pyinstaller
   ```
2. Build the executable:
   ```bash
   pyinstaller --onefile --name network-info run.py
   ```
3. The launcher exe will be generated in the `dist/` directory (e.g. `dist/network-info.exe`).

You can then invoke:
```bash
dist/network-info.exe dev
dist/network-info.exe report -rf html -o report.html
```