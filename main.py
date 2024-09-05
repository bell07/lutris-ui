import pygame

from controls import Controls
from ui import Ui

if __name__ == '__main__':
    ui = Ui()
    ctr = Controls()

    while ctr.is_running:
        ctr.update_controls()
        if ctr.is_running is False:
            break

        ui.process_controls(ctr)
        ui.draw()

    pygame.quit()
