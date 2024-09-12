import pygame

REPEAT_TIME_1 = 500  # ms
REPEAT_TIME_2 = 200  # ms

JS_REPEATABLE_MAP = (pygame.CONTROLLER_BUTTON_A, pygame.CONTROLLER_BUTTON_B, pygame.CONTROLLER_BUTTON_DPAD_UP,
                     pygame.CONTROLLER_BUTTON_DPAD_DOWN, pygame.CONTROLLER_BUTTON_DPAD_LEFT,
                     pygame.CONTROLLER_BUTTON_DPAD_RIGHT)


# UI Controls proxy
class Controls:
    def __init__(self):
        self.events = None

        self._clock = pygame.time.Clock()
        pygame.key.set_repeat(REPEAT_TIME_1, REPEAT_TIME_2)
        self._timer1 = 0  # Timer 1 since key is pressed
        self._timer2 = None  # Timer 2 since key was processed last time
        self._pressed_key = None  # Pressed key

    @staticmethod
    def init_all_js():
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

    def _release(self):
        self._pressed_key = None

    def _get_repeated_key(self):
        # Nothing pressed
        if self._pressed_key is None:
            return None

        # Check for Timer 1
        self._timer1 = self._timer1 + self._clock.get_time()

        # Repeat time 1 not reached
        if self._timer1 < REPEAT_TIME_1 and self._timer2 is None:
            return None

        # Check for timer 2
        if self._timer2 is None:
            self._timer2 = 0
            return self._pressed_key
        else:
            self._timer2 = self._timer2 + self._clock.get_time()

            # Repeat time 2 not reached
        if self._timer2 < REPEAT_TIME_2:
            return None

        self._timer2 = self._timer2 % REPEAT_TIME_2
        return self._pressed_key

    def update_controls(self):
        self.events = pygame.event.get()
        for e in self.events:
            match e.type:
                case pygame.JOYDEVICEADDED:
                    js = pygame.joystick.Joystick(e.device_index)
                    self.init_all_js()
                    print(f"Joystick added: {str(js.get_name())}")

                case pygame.JOYDEVICEREMOVED:
                    print(f"Joystick removed: {e.instance_id}")
                    self.init_all_js()

                case pygame.JOYBUTTONDOWN:  # instance_id, button
                    if e.button in JS_REPEATABLE_MAP:
                        self._press(e.button)

                case pygame.JOYBUTTONUP:  # instance_id, button
                    self._release()

        repeated_key = self._get_repeated_key()
        if repeated_key is not None:
            print(f"Repeated {repeated_key}")

            self.events.append(pygame.event.Event(pygame.JOYBUTTONDOWN, {"button": repeated_key}))

    def game_tick(self):
        self._clock.tick(30)  # limits FPS to 30
