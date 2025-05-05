# Ping Overlay

A lightweight, always-on-top ping monitor for Windows that shows your network latency in real-time. Perfect for gamers, streamers, or anyone who needs to monitor their network connection without opening a command prompt.

![Ping Overlay Screenshot](screenshot.png)

## Features

- **Always on Top**: Stays visible above other windows
- **Customizable Position**: Drag anywhere or use preset positions
- **Color-coded Display**:
  - 🟢 Green: < 50ms (Good)
  - 🟡 Yellow: 50-100ms (Moderate)
  - 🔴 Red: > 100ms (Poor)
- **Draggable**: Click and drag to position anywhere
- **Compact Design**: Minimal UI that doesn't get in the way
- **Real-time Updates**: Updates every second
- **Corner Snapping**: Easily position in any corner
- **Semi-transparent**: See through to content below

## Quick Start

### Option 1: Download the Executable

1. Go to the [Releases](https://github.com/rainerat/PingOverlay/releases) page
2. Download `ping_overlay.exe`
3. Run it!

### Option 2: Build from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/rainerat/PingOverlay.git
   cd PingOverlay
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python ping_overlay.py
   ```

## Usage

- **Move**: Click and drag the overlay
- **Position Presets**: Right-click → Position → Choose corner
- **Exit**: Right-click → Exit

## Customization

You can customize the overlay by modifying these variables in `ping_overlay.py`:

- `CORNER_MARGIN`: Distance from screen edges (default: 5 pixels)
- Font size and colors in the `setStyleSheet` section

## Building from Source

To create your own executable:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --icon=icon.ico ping_overlay.py
```

The executable will be in the `dist` folder.

## Running on Startup

### Method 1: Startup Folder

1. Press `Win + R`
2. Type `shell:startup`
3. Copy `ping_overlay.exe` to this folder

### Method 2: Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to "At log on"
4. Action: Start a program
5. Browse to `ping_overlay.exe`

## Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Ping functionality using [ping3](https://github.com/kyan001/ping3)
