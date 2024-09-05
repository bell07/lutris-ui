import pygame

REPEAT_TIME_1 = 500  # ms
REPEAT_TIME_2 = 200  # ms

JS_MAP = {
    pygame.CONTROLLER_BUTTON_A: "OK",
    pygame.CONTROLLER_BUTTON_B: "CANCEL",
    pygame.CONTROLLER_BUTTON_DPAD_UP: "UP",
    pygame.CONTROLLER_BUTTON_DPAD_DOWN: "DOWN",
    pygame.CONTROLLER_BUTTON_DPAD_LEFT: "LEFT",
    pygame.CONTROLLER_BUTTON_DPAD_RIGHT: "RIGHT",
}

# Keyboard
KBD_MAP = {
    pygame.K_RETURN: "OK",
    pygame.K_ESCAPE: "CANCEL",
    pygame.K_UP: "UP",
    pygame.K_DOWN: "DOWN",
    pygame.K_LEFT: "LEFT",
    pygame.K_RIGHT: "RIGHT",
  }


# UI Controls proxy
class Controls:
    def __init__(self):
        self.is_running = True  # False, if application should shutdown

        self._clock = pygame.time.Clock()
        self._timer1 = 0  # Timer 1 since key is pressed
        self._timer2 = None  # Timer 2 since key was processed last time

        self._pressed_key = None  # Pressed key
        self._is_pressed = False  # Key is pressed / hold
        self._is_reported = False  # Key press reported once already
        self.events = None

    def init_all_js(self):
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            pygame.joystick.Joystick(i).init()

    def _press(self, key):
        if self._pressed_key == key:
            pass  # Already pressed
        else:
            self._pressed_key = key
            self._timer1 = 0
            self._timer2 = None
            self._is_pressed = True
            self._is_reported = False

    def _release(self):
        if self._is_reported is True:
            self._pressed_key = None
        self._is_pressed = False

    def _report_value(self):
        self._is_reported = True
        return self._pressed_key

    def get_pressed_key(self):
        # Nothing pressed
        if self._pressed_key is None:
            return None

        # Key known, but not yet reported. Do it
        if self._is_reported is False:
            return self._report_value()

        # Not pressed anymore
        if self._is_pressed is False:
            self._release()
            return

        # Check for Timer 1
        self._timer1 = self._timer1 + self._clock.get_time()

        # Repeat time 1 not reached
        if self._timer1 < REPEAT_TIME_1 and self._timer2 is None:
            return None

        # Check for timer 2
        if self._timer2 is None:
            self._timer2 = 0
            return self._report_value()
        else:
            self._timer2 = self._timer2 + self._clock.get_time()

            # Repeat time 2 not reached
        if self._timer2 < REPEAT_TIME_2:
            return None

        self._timer2 = self._timer2 % REPEAT_TIME_2
        return self._report_value()

    def update_controls(self):
        self.events = pygame.event.get()
        for e in self.events:
            match e.type:
                case pygame.QUIT:
                    self.is_running = False
                    break

                case pygame.JOYDEVICEADDED:
                    js = pygame.joystick.Joystick(e.device_index)
                    self.init_all_js()
                    print(f"Joystick added: {str(js.get_name())}")

                case pygame.JOYDEVICEREMOVED:
                    print(f"Joystick removed: {e.instance_id}")
                    self.init_all_js()

                case pygame.KEYDOWN:  # key, mod, unicode, scancode
                    supported_key = KBD_MAP.get(e.key)
                    if supported_key is not None:
                        self._press(supported_key)
                case pygame.KEYUP:  # key, mod, unicode, scancode
                    self._release()
                    pass

                case pygame.JOYBUTTONDOWN:  # instance_id, button
                    supported_key = JS_MAP.get(e.button)
                    if supported_key is not None:
                        self._press(supported_key)

                case pygame.JOYBUTTONUP:  # instance_id, button
                    self._release()

                case pygame.MOUSEBUTTONDOWN:  # pos, button, touch
                    print("MOUSEBUTTONDOWN", e.pos, e.button)
                case pygame.MOUSEBUTTONUP:  # pos, button, touch
                    print("MOUSEBUTTONUP", e.pos, e.button)

                case pygame.MOUSEMOTION:  # pos, rel, buttons, touch
                    # TODO: mouseover event.pos, rel, buttons
                    pass
                case pygame.JOYHATMOTION:  # instance_id, hat, value
                    print("Joystick HAT moved")
                case pygame.JOYBALLMOTION:  # instance_id, ball, rel
                    print("Joystick BALL? moved")
                case pygame.JOYAXISMOTION:  # instance_id, axis, value
                    print("Joystick axis moved")
