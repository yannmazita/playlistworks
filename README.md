# playlistworks

Work in progress! Very early stage and actively developed.

`playlistworks` is a playlist-driven music player built with Python and [QT/QML](https://doc.qt.io/qt-6/qmlreference.html).

![playlistworks_capture](https://github.com/user-attachments/assets/48298068-6892-43d9-b716-6cdd47767116)


## Getting Started

1.  Clone the repository:

    ```bash
    git clone https://github.com/yannmazita/playlistworks.git
    ```

2.  Activate virtual environment, install dependencies:

    ```bash
    eval $(poetry env activate)
    poetry install
    ```

3.  Start the application

    ```bash
    python -m src.main
    ```

## Dependencies

- PySide6 (QT6 Python bindings)
- mutagen (Audio metadata)

## Roadmap (MVP)
- Metadata extraction and database: ✅
- Audio file player: ✅
- GUI: 🕙
- Regex dynamic playlists: ❌

## Goals
- Robust and fast dynamic playlist creation using audio file metadata
- Desktop and Mobile ports

## Contributing

Contributions are welcome!
