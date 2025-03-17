// src/features/playlists/utils/qmlUtils.js

export function showPlaylist(playlistId) {
  songTableView.inPlaylistMode = true;
  songTableView.currentPlaylistId = playlistId;
  backend.setCurrentPlaylist(playlistId);
};
