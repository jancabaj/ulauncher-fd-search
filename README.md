# Fast File Search for Ulauncher

A blazing fast file and folder search extension for Ulauncher using `fd`.

## Features

- Search files and folders as you type
- Real-time results (no database needed)
- Searches entire home directory and subdirectories
- Fast and efficient using `fd` tool
- Opens files with default application
- Opens folders in file manager

## Requirements

- Ulauncher 5+
- `fd` tool installed (`sudo apt install fd-find`)

## Installation

1. Clone or copy this directory to Ulauncher extensions folder:
   ```bash
   ln -s /home/cabaj/ulauncher-fd-search ~/.local/share/ulauncher/extensions/ulauncher-fd-search
   ```

2. Restart Ulauncher or go to Preferences → Extensions → Add extension

## Usage

1. Open Ulauncher (default: `Ctrl+Space`)
2. Type `fd` (or your configured keyword) followed by search term
3. Example: `fd myproject` - searches for files/folders containing "myproject"
4. Select result to open file or folder

## Configuration

- **Keyword**: Change the trigger keyword (default: `fd`)
- **Search Path**: Change base directory to search (default: `~`)
- **Max Results**: Maximum number of results to display (default: 10)

## Tips

- Type at least 2 characters to start searching
- Search is case-insensitive by default
- Searches both file names and folder names
- Results include full path in description
