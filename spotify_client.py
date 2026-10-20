# Everything that talks to spotify
import time
import logging
import socket
from io import BytesIO
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pygame
import requests

import config
import state


scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, open_browser=False, cache_path="/home/willh/.spotipy_cache"))

consecutive_failures = 0
current_track_id = None
request_timestamps = []
network_down_logged = False
rate_limit_active = False

def network_is_up():
	global network_down_logged
	try:
		socket.getaddrinfo("api.spotify.com", 443)
	except OSError:
		if not network_down_logged:
			logging.warning("Network not available, waiting")
			network_down_logged = True
		return False
	
	if network_down_logged:
		logging.info("Network available")
		network_down_logged = False
	return True


def check_rate_limit_status():
	try:
		sp.current_user()
		print("API access is working, no rate limit active")
	except spotipy.exceptions.SpotifyException as e:
		logging.error(f"API Limit error: {e}")
		print(f"Still rate limited or another error occured: {e}")


def fetch_track_data():
	global current_track_id, consecutive_failures

	if not network_is_up():
		return
		
	if not can_make_requests():
		return
	
	request_timestamps.append(time.time())

	try:
		current = sp.current_playback()
		consecutive_failures = 0
	except (spotipy.exceptions.SpotifyException, requests.exceptions.RequestException) as e:
		logging.error(f"Polling error: {e}")
		consecutive_failures += 1
		wait_time = min(consecutive_failures * 2, 60)
		logging.info(f"Backing off for {wait_time}s after {consecutive_failures} consecutive failures")
		time.sleep(wait_time)
		return
	
	if current and current['item']:
		track_id = current['item']['id']
		if track_id != current_track_id:
			current_track_id = track_id
			art_url = current['item']['album']['images'][0]['url']
			state.album_art = get_album_art(art_url, 180)
		
		state.title = current['item']['name']
		state.artist = " & ".join(a['name'] for a in current['item']['artists'][:2])
		state.progress = current['progress_ms']
		state.duration = current['item']['duration_ms']
		state.is_playing = current['is_playing']
	else:
		state.title = "Nothing Playing"
		state.artist = ""
		state.is_playing = False


def can_make_requests():
	global request_timestamps, rate_limit_active
	now = time.time()
	
	request_timestamps = [t for t in request_timestamps if now - t < config.WINDOW_SECONDS]
	
	if len(request_timestamps) < config.MAX_REQUESTS_PER_WINDOW:
		if rate_limit_active:
			logging.info("Self-imposed rate limit cleared")
			rate_limit_active = False
		return True
	
	if not rate_limit_active:
		logging.warning("Self-imposed rate limit reached, skipping requests until it clears ")
		rate_limit_active = True
	return False


def polling_loop():
	while True:
		fetch_track_data()
		time.sleep(config.POLL_INTERVAL)


def get_album_art(url, size):
	try:
		response = requests.get(url, timeout = 5)
		image_data = BytesIO(response.content)
		image = pygame.image.load(image_data)
		image = pygame.transform.scale(image, (size, size))
		return image
	except (requests.exceptions.RequestException, pygame.error) as e:
		logging.error(f"Album art error: {e}")
		return None

