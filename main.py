import pygame

from controls import Controls
from ui import Ui

if __name__ == '__main__':
    ui = Ui()
    ctr = Controls()

    while True:
        ctr.update_controls()
        if ui.process_controls(ctr) is False:
            break
        ui.draw_ui()
        ctr.game_tick()

    pygame.quit()
