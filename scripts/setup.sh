#!/bin/bash

set -e

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# --- Check for Poetry ---
if ! command_exists poetry; then
  echo "Error: Poetry is not installed. Please install it:"
  echo "https://python-poetry.org/docs/#installation"
  exit 1
fi

# --- Check for GStreamer ---
if ! command_exists gst-launch-1.0; then
  echo "Error: GStreamer is not installed. Please install it:"
  echo "Fedora: sudo dnf install gstreamer1-devel gstreamer1-plugins-base gstreamer1-plugins-good gstreamer1-plugins-bad-free gstreamer1-plugins-ugly python3-gobject"
  echo "Arch Linux: sudo pacman -S gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly gst-libav python-gobject
"
  exit 1
fi

# --- Find system Python (with GStreamer) ---
SYSTEM_PYTHON=$(which python3)
if [ -z "$SYSTEM_PYTHON" ]; then
  echo "Error: Could not find system Python 3 interpreter."
  exit 1
fi

# --- Set up Poetry environment ---
echo "Setting up Poetry environment..."

# Use the system Python interpreter.
poetry env use "$SYSTEM_PYTHON"

# Install dependencies
poetry install

echo "Setup complete! Activate the environment with: $(eval poetry env activate)"
