# Handles everything that draws
import pygame
import numpy as np

import config
import state


surface = pygame.Surface((config.WIDTH, config.HEIGHT))

scroll_offset = 0
scroll_direction = 1

def format_time(ms):
	total_seconds = ms // 1000
	minutes = total_seconds // 60
	seconds = total_seconds % 60
	return f"{minutes}:{seconds:02d}"


def render_frame():
	global scroll_offset, scroll_direction
	surface.fill(config.DARK_BLUE)

	title, artist, album_art, progress, duration, is_playing = state.title, state.artist, state.album_art, state.progress, state.duration, state.is_playing

  # Artist and name info
	full_text = f"{title} - {artist}"
	text_surface = config.font_large.render(full_text, True, config.WHITE)
	text_width = text_surface.get_width()

	# Scrolling text mechs
	if text_width <= config.MAX_TEXT_WIDTH:
		text_rect = text_surface.get_rect(center = (config.WIDTH // 2, 210))
		surface.blit(text_surface, text_rect)
	else:
		overflow = text_width - config.MAX_TEXT_WIDTH
		scroll_offset += scroll_direction * config.SCROLL_SPEED

		if scroll_offset >= overflow:
			scroll_offset = overflow
			scroll_direction = -1
		elif scroll_offset <= 0:
			scroll_offset = 0
			scroll_direction = 1
	
		text_area = pygame.Rect((config.WIDTH - config.MAX_TEXT_WIDTH) // 2, 190, config.MAX_TEXT_WIDTH, 40)

		surface.set_clip(text_area)
		surface.blit(text_surface, (text_area.x - scroll_offset, 200))
		surface.set_clip(None)

	if album_art:
		surface.blit(album_art, (152, 15))
	else:
		pygame.draw.rect(surface, config.GRAY, (152, 15, 180, 180))

	# Song Clock
	time_text = f"{format_time(progress)}/{format_time(duration)}"
	time_surface = config.font_small.render(time_text, True, config.GRAY)
	time_rect = time_surface.get_rect()
	time_rect.topright = (config.WIDTH - 15, 10)
	surface.blit(time_surface, time_rect)

	# Play/Pause buttons
	if is_playing:
		pygame.draw.rect(surface, config.BLACK, (223, 245, 12, 46)) # Left Bar (x, y, width, height)
		pygame.draw.rect(surface, config.BLACK, (247, 245, 12, 46)) # Right Bar
	else:	
		play_button_points = [(222.25, 244.875), (222.25, 291.125), (260.5, 267.5)] # x1, y1,  x2, y2,  x3, y3
		pygame.draw.polygon(surface, config.BLACK, play_button_points)

	# Back button
	pygame.draw.polygon(surface, config.BLACK, config.back_button_points)

	back_line_start = (70, 250)
	back_line_end = (70, 285)
	pygame.draw.line(surface, config.BLACK, back_line_start, back_line_end, width = 3)

	# Skip button
	pygame.draw.polygon(surface, config.BLACK, config.skip_button_points)

	next_line_start = (410, 250)
	next_line_end = (410, 285)
	pygame.draw.line(surface, config.BLACK, next_line_start, next_line_end, width = 3)


def push_to_display():
	rotated_surface = pygame.transform.rotate(surface, 180)
	pixels = pygame.surfarray.array3d(rotated_surface)
	pixels = np.transpose(pixels, (1, 0, 2))
	r = (pixels[:, :, 0] >> 3).astype(np.uint16)
	g = (pixels[:, :, 1] >> 2).astype(np.uint16)
	b = (pixels[:, :, 2] >> 3).astype(np.uint16)
	rgb565 = (r << 11) | (g << 5) | b
	with open('/dev/fb0', 'wb') as fb:
			fb.write(rgb565.astype(np.uint16).tobytes())
