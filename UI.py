import sys
import os
import asyncio
import pygame
from human_three.play_3 import play_3
from human_four.play_4 import play_4
from human_two.play_2 import play_2
from utils.utils import Button

def main():
    pygame.init()

    # Define constants
    WIDTH, HEIGHT = 800, 800
    ROWS, COLS = 4, 4

    # Set up the display
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Custom Tactical Board Game')

    # Load images and fonts directly
    WELCOME_BG_IMAGE = pygame.transform.scale(
        pygame.image.load('assets/welcome_background.png'), (800, 800)
    )
    FONT = pygame.font.Font('assets/fonts/Roboto-Bold.ttf', 36)
    TEXT_COLOR = (255, 255, 255)

    running = True

    # Create buttons
    start_button = Button('Play 2', (WIDTH // 2 - 100, HEIGHT // 2 - 50), (200, 50), play_2)
    # bot_button = Button('Play bot', (WIDTH // 2 - 100, HEIGHT // 2 + 20), (200, 50), bot_AI)
    play_3_button = Button('Play 3', (WIDTH // 2 - 100, HEIGHT // 2 + 90), (200, 50), play_3)
    play_4_button = Button('Play 4', (WIDTH // 2 - 100, HEIGHT // 2 + 160), (200, 50), play_4)

    # Instead of sys.exit, we’ll handle exiting gracefully
    def exit_game():
        nonlocal running
        running = False

    exit_button = Button('Exit', (WIDTH // 2 - 100, HEIGHT // 2 + 230), (200, 50), exit_game)

    clock = pygame.time.Clock()

    while running:
        WIN.blit(WELCOME_BG_IMAGE, (0, 0))
        title_text = FONT.render('Tactical Formation Game', True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
        WIN.blit(title_text, title_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            start_button.handle_event(event)
            exit_button.handle_event(event)
            play_3_button.handle_event(event)
            play_4_button.handle_event(event)
            # bot_button.handle_event(event)

        start_button.draw(WIN)
        exit_button.draw(WIN)
        play_3_button.draw(WIN)
        play_4_button.draw(WIN)
        # bot_button.draw(WIN)

        pygame.display.update()
        clock.tick(60)
        
        # Yield to the browser event loop
        # await asyncio.sleep(0)

if __name__ == '__main__':
    main()