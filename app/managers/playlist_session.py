import uuid
from typing import List
from managers.music_session import MusicSession
from models import PlaylistElement, PlayListSessionStatus

class PlaylistSession:
    def __init__(self, name: str = None, volume: float = 1.0):
        self.name = name
        self.session_id = str(uuid.uuid4())
        self.playlist = []  # List of PlaylistElement
        self.current_index = 0
        self.current_session = None  # 当前的 MusicSession
        self.status = "created"
        self.volume = volume
        
    def add_songs(self, songs: List[PlaylistElement]):
        """添加歌曲到播放列表"""
        self.playlist.extend(songs)
        
    def play(self):
        """播放列表中的歌曲"""
        if not self.playlist:
            return False
        return self.play_index(self.current_index)
    
    def play_index(self, index: int):
        """播放指定位置的歌曲"""
        if index < 0 or index >= len(self.playlist):
            return False
            
        # 停止当前播放
        if self.current_session:
            self.current_session.stop()
            
        # 创建新的 MusicSession
        song = self.playlist[index]
        self.current_session = MusicSession(
            url=song.url, 
            volume=self.volume
        )
        self.current_index = index
        self.status = "playing"
        return self.current_session.play()
        
    def next(self):
        """下一首"""
        if not self.playlist:
            return False
        next_index = (self.current_index + 1) % len(self.playlist)
        return self.play_index(next_index)
        
    def prev(self):
        """上一首"""
        if not self.playlist:
            return False
        prev_index = (self.current_index - 1) % len(self.playlist)
        return self.play_index(prev_index)
        
    # 代理当前 MusicSession 的方法
    def pause(self):
        if self.current_session:
            result = self.current_session.pause()
            if result:
                self.status = "paused"
            return result
        return False
        
    def resume(self):
        if self.current_session:
            result = self.current_session.resume()
            if result:
                self.status = "playing"
            return result
        return False
        
    def stop(self):
        if self.current_session:
            result = self.current_session.stop()
            if result:
                self.status = "stopped"
            return result
        return False
        
    def set_volume(self, volume: float):
        self.volume = volume
        if self.current_session:
            return self.current_session.set_volume(volume)
        return True
    
    def get_status(self) -> PlayListSessionStatus:
        """获取播放列表的状态"""
        current_song_status = None
        is_playing = False
        
        if self.current_session:
            # 获取当前歌曲的详细状态
            current_song_status = self.current_session.get_status()
            is_playing = (self.current_session.status == "playing" and 
                         not self.current_session._is_paused)
        
        return PlayListSessionStatus(
            session_id=self.session_id,
            status=self.status,
            playlist=self.playlist,
            current_index=self.current_index,
            current_song_status=current_song_status,
            volume=self.volume,
            is_playing=is_playing,
            playlist_length=len(self.playlist)
        )