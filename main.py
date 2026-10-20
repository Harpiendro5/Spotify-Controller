import time
import logging
from logging.handlers import RotatingFileHandler
import threading

import config
import state
import touch
import display
import spotify_client


handler = RotatingFileHandler('/home/willh/controller.log', maxBytes = 1_000_000, backupCount = 2)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', handlers = [handler])

polling_thread = threading.Thread(target = spotify_client.polling_loop, daemon = True)
polling_thread.start()

last_render_time = 0
running = True

while running:
	touch.check_touch()

	now = time.time()
	if now - last_render_time >= config.RENDER_INTERVAL:
		last_render_time = now
		display.render_frame()
		display.push_to_display()

	time.sleep(0.05)

