# playlistworks

Work in progress! Very early stage and actively developed.

`playlistworks` is a playlist-driven music player built with Python and [QT/QML](https://doc.qt.io/qt-6/qmlreference.html).

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

- SQLAlchemy (Python ORM)
- PySide6 (QT6 Python bindings)
- mutagen (Audio metadata)
- pygobject (GObject Python bindings)

## Goals
- Robust and fast dynamic playlist creation using audio file metadata
- Desktop and Mobile ports

## Non-goals
- Tagging (See [Ex Falso](https://github.com/quodlibet/quodlibet) part of the Quod Libet project)
- Library management

## Contributing

Contributions are welcome!
