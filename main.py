import sys
import os
import asyncio
import pygame
from human_three.play_3 import play_3
from human_four.play_4 import play_4
from human_two.play_2 import play_2
from human_two.bot_AI import bot_AI
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

    current_screen = "menu"  # Add variable state
    clock = pygame.time.Clock()

    async def exit_game():
        return "exit"

    async def start_game_2():
        return "play_2"
    
    async def start_game_bot():
        return "bot_AI"

    async def start_game_3():
        return "play_3"

    async def start_game_4():
        return "play_4"

    start_button = Button('Play 2', (WIDTH // 2 - 100, HEIGHT // 2 - 50), (200, 50), start_game_2)
    bot_button = Button('Bot AI', (WIDTH // 2 - 100, HEIGHT // 2 + 20), (200, 50), start_game_bot)
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
                
                # Handle callbacks for all buttons
                callback = start_button.handle_event(event)
                if callback:
                    current_screen = await callback()

                callback = bot_button.handle_event(event)
                if callback:
                    current_screen = await callback()

                callback = play_3_button.handle_event(event)
                if callback:
                    current_screen = await callback()

                callback = play_4_button.handle_event(event)
                if callback:
                    current_screen = await callback()

                callback = exit_button.handle_event(event)
                if callback:
                    current_screen = await callback()

            start_button.draw(WIN)
            bot_button.draw(WIN)
            play_3_button.draw(WIN)
            play_4_button.draw(WIN)
            exit_button.draw(WIN)

        elif current_screen == "play_2":
            current_screen = await play_2()
        
        elif current_screen == "bot_AI":
            current_screen = await bot_AI()

        elif current_screen == "play_3":
            current_screen = await play_3()

        elif current_screen == "play_4":
            current_screen = await play_4()

        elif current_screen == "exit":
            break

        pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == '__main__':
    asyncio.run(main())



