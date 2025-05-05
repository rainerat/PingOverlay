# Ping Overlay

A lightweight ping overlay application that stays on top of other windows and shows your ping to Google.com in real-time.

## Features

- Always-on-top transparent window
- Real-time ping monitoring
- Color-coded ping display (green < 50ms, yellow < 100ms, red > 100ms)
- Draggable window
- Position presets (Top Left, Top Right, Bottom Left, Bottom Right)
- Right-click menu for easy exit

## Setup

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:

   ```
   python ping_overlay.py
   ```

2. The overlay will appear in the top-left corner by default
3. You can:
   - Drag the window to any position
   - Use the position buttons to quickly move to preset positions
   - Right-click to access the exit menu
   - The ping updates every second automatically

## Notes

- The overlay is semi-transparent with a dark background
- Ping values are color-coded for easy monitoring
- The window will stay on top of other applications
