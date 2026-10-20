
import os
import json
import base64
import random
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

PLAYLIST_ID = "3GQp28YEVzWDuaD9LfbqYd"

def request(url, data=None, headers=None):
    req = urllib.request.Request(
        url,
        data=data,
        headers=headers or {},
        method="POST" if data is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

def main():
    client_id = os.environ["SPOTIFY_CLIENT_ID"]
    client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]
    refresh_token = os.environ["SPOTIFY_REFRESH_TOKEN"]

    basic = base64.b64encode(
        f"{client_id}:{client_secret}".encode()
    ).decode()

    token_data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }).encode()

    token = request(
        "https://accounts.spotify.com/api/token",
        token_data,
        {"Authorization": f"Basic {basic}",
         "Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = token["access_token"]

    url = (
        f"https://api.spotify.com/v1/playlists/"
        f"{PLAYLIST_ID}/items?limit=50"
    )
    data = request(url, headers={
        "Authorization": f"Bearer {access_token}"
    })

    songs = []
    for entry in data.get("items", []):
        track = entry.get("item") or entry.get("track")
        if not track or track.get("type") != "track":
            continue
        artists = ", ".join(
            artist["name"] for artist in track.get("artists", [])
        )
        link = track.get("external_urls", {}).get("spotify", "")
        if track.get("name") and artists and link:
            songs.append({
                "name": track["name"],
                "artists": artists,
                "url": link,
            })

    if not songs:
        raise RuntimeError(
            "추천할 곡이 없습니다. 재생목록 접근 권한을 확인하세요."
        )

    now = datetime.now(ZoneInfo("Asia/Seoul"))
    if now.hour < 12:
        mood = "아침 추천곡 ☀️"
    else:
        mood = "퇴근 추천곡 🌇"

    song = random.choice(songs)
    print(f"🎵 {mood}")
    print(f"곡: {song['name']}")
    print(f"아티스트: {song['artists']}")
    print(f"Spotify: {song['url']}")

if __name__ == "__main__":
    main()
