import os
from evdev import InputDevice, ecodes
import pygame


touch_x, touch_y = None, None

touch_dev = InputDevice('/dev/input/event2')
touch_dev.grab()
os.set_blocking(touch_dev.fd, False)

back_zone = pygame.Rect(700, 750, 350, 250)
pause_zone = pygame.Rect(700, 1900, 350, 250)
skip_zone = pygame.Rect(700, 3100, 350, 250)


def handle_touch(raw_x, raw_y):
	point = (raw_x, raw_y)
	if back_zone.collidepoint(point):
		print(f"Back initiated at points: {point}")
	elif pause_zone.collidepoint(point):
		print(f"Pause/Play initiated at points: {point}")
	elif skip_zone.collidepoint(point):
		print(f"Skip initiated at points: {point}")


def check_touch():
	global touch_x, touch_y
	try:
		events = touch_dev.read()
		for event in events:
			if event.type == ecodes.EV_ABS:
				if event.code == ecodes.ABS_X:
					touch_x = event.value
				elif event.code == ecodes.ABS_Y:
					touch_y = event.value
			elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH: 
				if event.value == 1 and touch_x is not None and touch_y is not None:
					handle_touch(touch_x, touch_y)
	except BlockingIOError:
		pass

