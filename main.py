import pygame
from controls import Controls

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Lutris-UI")
    screen = pygame.display.set_mode((1280, 720))  # TODO: Fullscreen with native resolution

    clock = pygame.time.Clock()
    ctr = Controls(clock)

    while ctr.is_running:
        ctr.update_controls()
        # Fill the background with white
        screen.fill((255, 255, 255))

        key = ctr.get_pressed_key()
        if key is not None:
            print(f"Pressed key: {key}")
        # Flip the display
        pygame.display.flip()
        clock.tick(60)  # limits FPS to 30

    pygame.quit()
