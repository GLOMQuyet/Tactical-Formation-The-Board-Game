import sys
import os
import asyncio
import pygame
from human_three.play_3 import play_3
from human_four.play_4 import play_4
from human_two.play_2 import play_2
from utils.utils import Button


async def main():
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

    global current_screen
    current_screen = "menu"  # Add variable state
    clock = pygame.time.Clock()

    def exit_game():
        global current_screen
        current_screen = "exit"

    async def start_game_2():
        global current_screen
        current_screen = "play_2"
    
    async def start_game_3():
        global current_screen
        current_screen = "play_3"
    
    async def start_game_4():
        global current_screen
        current_screen = "play_4"

    start_button = Button('Play 2', (WIDTH // 2 - 100, HEIGHT // 2 - 50), (200, 50), start_game_2)
    play_3_button = Button('Play 3', (WIDTH // 2 - 100, HEIGHT // 2 + 90), (200, 50), start_game_3)
    play_4_button = Button('Play 4', (WIDTH // 2 - 100, HEIGHT // 2 + 160), (200, 50), start_game_4)
    exit_button = Button('Exit', (WIDTH // 2 - 100, HEIGHT // 2 + 230), (200, 50), exit_game)

    while True:
        clock.tick(120)
        if current_screen == "menu":
            WIN.blit(WELCOME_BG_IMAGE, (0, 0))
            title_text = FONT.render('Tactical Formation Game', True, TEXT_COLOR)
            title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
            WIN.blit(title_text, title_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    current_screen = "exit"
                
                # Xử lý callback cho tất cả các button
                callback = start_button.handle_event(event)
                if callback:
                    await callback()

                callback = play_3_button.handle_event(event)
                if callback:
                    await callback()

                callback = play_4_button.handle_event(event)
                if callback:
                    await callback()

                callback = exit_button.handle_event(event)
                if callback:
                  callback()

            start_button.draw(WIN)
            play_3_button.draw(WIN)
            play_4_button.draw(WIN)
            exit_button.draw(WIN)

        elif current_screen == "play_2":
            await play_2()
        
        elif current_screen == "play_3":
            await play_3()
        elif current_screen == "play_4":
            await play_4()

        elif current_screen == "exit":
            break

        pygame.display.update()
        await asyncio.sleep(0)


    pygame.quit()
     
if __name__ == '__main__':
    asyncio.run(main())