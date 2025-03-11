# src.features.player.types

from enum import Enum


class PlaybackState(Enum):
    StoppedState = 0
    PlayingState = 1
    PausedState = 2
