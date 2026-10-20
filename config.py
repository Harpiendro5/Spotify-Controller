import pygame


pygame.font.init()

WIDTH, HEIGHT = 480, 320

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_BLUE = (30, 42, 55)

font_large = pygame.font.SysFont(None, 36)
font_small = pygame.font.SysFont(None, 28)

# Scrolling variables
MAX_TEXT_WIDTH = WIDTH - 40
SCROLL_SPEED = 40

RENDER_INTERVAL = 0.7
POLL_INTERVAL = 1.5

# Time out variables
MAX_REQUESTS_PER_WINDOW = 60
WINDOW_SECONDS = 60

back_button_points = [(95, 250), (95, 285), (70, 267.5)]
skip_button_points = [(385, 250), (385, 285), (410, 267.5)]
