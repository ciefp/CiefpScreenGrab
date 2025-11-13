
# CiefpScreenGrab

![Enigma2](https://img.shields.io/badge/Enigma2-Plugin-blue)
![Python](https://img.shields.io/badge/Python-2.7%2B%20%7C%203.x-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Screenshots](https://img.shields.io/badge/Screenshots-JPG%20%7C%20PNG-success)
![Remote](https://img.shields.io/badge/Remote%20Control-Hotkey-orange)

> **Instant screenshots of your Enigma2 interface – with one button press**

`CiefpScreenGrab` is a lightweight Enigma2 plugin that lets you **capture your current screen** instantly. Perfect for creating tutorials, reporting bugs, or sharing your custom skin.

---

## Features

- **One-click screenshot** (configurable hotkey)
- **Multiple formats**: `JPG` (smaller) or `PNG` (lossless)
- **Custom save path** (USB, HDD, `/tmp`, etc.)
- **Auto-naming**: `screenshot_YYYYMMDD_HHMMSS.jpg`
- **Silent mode** – no popups, just a flash
- **Remote control support** (via `TEXT` or custom key)
- **No dependencies** – pure Python + Enigma2 API

---

## User Guide

**[Full English Usage Guide (HTML Preview)](https://htmlpreview.github.io/?https://raw.githubusercontent.com/ciefp/CiefpScreenGrab/refs/heads/main/CiefpScreenGrab_Usage_Guide_EN.html)**

> Detailed step-by-step instructions, configuration tips, and examples.

---

## Screenshots


| ![Main](https://github.com/ciefp/CiefpScreenGrab/blob/main/screenshot1.jpg) |
| ![Preview](https://github.com/ciefp/CiefpScreenGrab/blob/main/screenshot2.jpg) |
| ![Files](https://github.com/ciefp/CiefpScreenGrab/blob/main/screenshot2.jpg) |
---

## Installation

### Method 1: Manual (Recommended)

```bash
# Download
wget https://github.com/ciefp/CiefpScreenGrab/archive/refs/heads/main.zip
unzip main.zip

# Copy plugin
scp -r CiefpScreenGrab-main/usr/lib/enigma2/python/Plugins/Extensions/CiefpScreenGrab root@your-box-ip:/usr/lib/enigma2/python/Plugins/Extensions/

# Restart Enigma2
init 4 && sleep 2 && init 3
```

### Method 2: IPK (Coming Soon)
```bash
opkg install ciefp-screengrab_*.ipk
```

---

## Usage

### Default Hotkey
- Press **`TEXT`** button on remote → **Screenshot saved!**

### Menu Access
- **Menu → Extensions → CiefpScreenGrab**
- Press **Green** to capture

### Saved Location
```
/media/hdd/screenshots/screenshot_20250405_143022.jpg
```

> Folder created automatically on first use.

---

## Configuration

| Option | Default | Description |
|-------|--------|-----------|
| **Format** | `JPG` | `JPG` (smaller) or `PNG` (transparent) |
| **Path** | `/media/hdd/screenshots/` | Any writable path |
| **Hotkey** | `TEXT` | Change to `INFO`, `PVR`, etc. |
| **Flash** | `ON` | Brief screen flash on capture |

> Edit config: `/etc/enigma2/ciefp_screengrab.conf` (created on first run)

---

## File Structure

```
usr/lib/enigma2/python/Plugins/Extensions/CiefpScreenGrab/
├── plugin.py
├── icon.png
├── CiefpScreenGrab_Usage_Guide_EN.html
└── locale/
    └── en/
        └── LC_MESSAGES/
            └── CiefpScreenGrab.po
```

---

## Example Output

```bash
/media/hdd/screenshots/
├── screenshot_20250405_140512.jpg
├── screenshot_20250405_142233.png
└── screenshot_20250405_143022.jpg
```

---

## Troubleshooting

| Issue | Solution |
|------|----------|
| No folder created | Check write permissions on target path |
| Black screenshot | Ensure GUI is not in standby |
| Hotkey not working | Re-assign in **Menu → Setup → System → Remote Control** |
| No flash | Some skins disable screen flash |

---

## Contributing

Help us improve!

1. Fork the repo
2. Create branch: `git checkout -b feature/web-upload`
3. Commit & push
4. Open **Pull Request**

**Ideas**:
- Upload to FTP/Imgur
- Add watermark
- Burst mode (3 shots)
- Web interface trigger

---

## Author

- **ciefp** – [GitHub Profile](https://github.com/ciefp)
- Found a bug? [Open an Issue](https://github.com/ciefp/CiefpScreenGrab/issues)

---

## License

```plaintext
MIT License © 2025 ciefp
```

> Free to use, modify, and share.

---

## Star the Project

Like it? Star it on GitHub!

[![GitHub stars](https://img.shields.io/github/stars/ciefp/CiefpScreenGrab?style=social)](https://github.com/ciefp/CiefpScreenGrab)

---

> **Pro Tip**: Assign `TEXT` button in remote settings for **instant screenshots anywhere**!

---

### Optional Files to Add

| File | Purpose |
|-----|--------|
| `LICENSE` | MIT license |
| `docs/screenshots/` | Real plugin screenshots |
| `icon.png` | 100x100 plugin icon |
| `CHANGELOG.md` | Version history |
| `.ipk` package | Easy install |

**Want me to generate any of these?** Just say the word!

---

**Spreman za GitHub!**  
Sada ima i **direktan link na tvoje englesko uputstvo** — korisnici će moći da ga otvore odmah, bez preuzimanja.

> **Link u README-u**:  
> [https://htmlpreview.github.io/?https://raw.githubusercontent.com/ciefp/CiefpScreenGrab/refs/heads/main/CiefpScreenGrab_Usage_Guide_EN.html](https://htmlpreview.github.io/?https://raw.githubusercontent.com/ciefp/CiefpScreenGrab/refs/heads/main/CiefpScreenGrab_Usage_Guide_EN.html)

Ako želiš, mogu ti napraviti i:
- Prevod uputstva na srpski
- PDF verziju
- Automatski generisani `.ipk`
- `LICENSE` fajl

Samo reci!