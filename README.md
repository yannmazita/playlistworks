# playlistworks

Work in progress! Very early stage and actively developed.

`playlistworks` is a playlist-driven music player built with Python and [QT/QML](https://doc.qt.io/qt-6/qmlreference.html).

![playlistworks_capture](https://github.com/user-attachments/assets/23b35b53-2c08-413c-bd72-637e1cd6839e)




## Getting Started

### Prerequisites

1.  **Python 3.13**
2.  **Poetry:** Install [Poetry](https://python-poetry.org/docs/#installation).
3.  **GStreamer:**
    *   **Arch Linux**
        ```bash
        sudo pacman -S gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly gst-libav python-gobject
        ```
    *   **Fedora**
        ```bash
        sudo dnf install gstreamer1-devel gstreamer1-plugins-base gstreamer1-plugins-good gstreamer1-plugins-bad-free gstreamer1-plugins-ugly python3-gobject
        ```

### Setup

1.  Clone repository and run the setup script:
    
    ```bash
    git clone https://github.com/yannmazita/playlistworks.git
    cd playlistworks
    ./scripts/setup.sh
    ```
2.  Activate poetry environment
    ```bash
    eval $(poetry env activate)
    ```

## Roadmap (MVP)
- **Metadata extraction and database**: ✅
- **Dynamic playlists**: ✅
    *   Tokenizer, lexer, parser, SQL generator: ✅
    *   Handling of any metadata field in JSON: ✅
    *   Search field: ✅
    *   Instant response: ✅
- **Audio playback**: 🕙
    *   Play, skip forward/backward, seek: ✅
    *   Play all songs currently displayed: ✅
    *   Gapless playback: ❌
- **GUI**: 🕙
    *   Main window:  ✅
    *   Sorting: ❌
    *   Playlist edition: ❌
    *   Aesthetic refinements: ❌

## Goals
- Robust and fast dynamic playlist creation using audio file metadata
- Desktop and Mobile ports

## Contributing

Contributions are welcome!
