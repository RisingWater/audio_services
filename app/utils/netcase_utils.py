import requests
from typing import Optional
from config import settings

def get_song_name_by_id(song_id: str) -> str:
    """
    根据歌曲ID获取歌曲名称
    返回: 歌曲名称字符串，失败返回空字符串
    """
    try:
        url = f"{settings.NETCASE_API}/song/detail?ids={song_id}"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        songs = data.get('songs', [])
        
        if songs:
            return songs[0]['name']
        return ""
        
    except Exception as e:
        print(f"获取歌曲名称失败: {e}")
        return ""

def get_song_url_by_id(song_id: str) -> Optional[str]:
    """
    根据歌曲ID获取歌曲播放URL
    参数: song_id - 歌曲ID
    返回: 歌曲播放URL字符串，失败返回None
    """
    try:
        url = f"{settings.NETCASE_API}/song/url?id={song_id}"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        song_data = data.get('data', [])
        
        if song_data and song_data[0].get('url'):
            return song_data[0]['url']
        
        return None
        
    except Exception as e:
        print(f"获取歌曲URL失败: {e}")
        return None