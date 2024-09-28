import pygame

from settings import Settings

REPEATABLE = ("UP", "DOWN", "LEFT", "RIGHT")

KBD_MAP = {pygame.K_UP: "UP", pygame.K_DOWN: "DOWN", pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT",
           pygame.K_RETURN: "ENTER", pygame.K_ESCAPE: "EXIT"}

JOY_MAP = {pygame.CONTROLLER_BUTTON_A: "ENTER", pygame.CONTROLLER_BUTTON_START: "ENTER",
           pygame.CONTROLLER_BUTTON_DPAD_UP: "UP", pygame.CONTROLLER_BUTTON_DPAD_DOWN: "DOWN",
           pygame.CONTROLLER_BUTTON_DPAD_LEFT: "LEFT", pygame.CONTROLLER_BUTTON_DPAD_RIGHT: "RIGHT"}

COMMAND_EVENT = pygame.USEREVENT + 1


# UI Controls proxy
class Controls:
    def __init__(self):
        self.events = None
        settings = Settings("input")
        self.repeat_time_1 = settings.get("repeat_time_1", 500)  # ms
        self.repeat_time_2 = settings.get("repeat_time_2", 200)  # ms

        self._clock = pygame.time.Clock()
        self._timer1 = 0  # Timer 1 since key is pressed
        self._timer2 = None  # Timer 2 since key was processed last time
        self._pressed_command = None
        self._pressed_event = None

    @staticmethod
    def init_all_js() -> None:
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            pygame.joystick.Joystick(i).init()

    @staticmethod
    def _is_same(event1: pygame.event.Event, event2: pygame.event.Event) -> bool:
        if event1.type != event2.type:  # Different types
            if (event1.type == pygame.KEYDOWN and event2.type == pygame.KEYUP) or (
                    event2.type == pygame.KEYDOWN and event1.type == pygame.KEYUP):
                return True

            if (event1.type == pygame.JOYBUTTONDOWN and event2.type == pygame.JOYBUTTONUP) or (
                    event2.type == pygame.JOYBUTTONDOWN and event1.type == pygame.JOYBUTTONUP):
                return True

            return False
        if event1.type == pygame.JOYAXISMOTION and event1.axis != event2.axis:  # Different axis
            return False

        return True

    def _press(self, command: str, event: pygame.event.Event) -> bool:
        if self._pressed_command == command and self._is_same(self._pressed_event, event):
            return False
        else:
            self._pressed_command = command
            self._pressed_event = event
            self._timer1 = 0
            self._timer2 = None
            return True  # Pressed first time

    def _release(self, release_event: pygame.event.Event) -> None:
        if self._pressed_event is not None and self._is_same(release_event, self._pressed_event):
            self._pressed_command = None
            self._pressed_event = None

    def _get_repeated_key(self) -> pygame.event.Event | None:
        # Nothing pressed
        if self._pressed_command is None:
            return None

        # Check for Timer 1
        self._timer1 = self._timer1 + self._clock.get_time()

        # Repeat time 1 not reached
        if self._timer1 < self.repeat_time_1 and self._timer2 is None:
            return None

        # Check for timer 2
        if self._timer2 is None:
            self._timer2 = 0
            return pygame.event.Event(COMMAND_EVENT, {"command": self._pressed_command, "origin": self._pressed_event})
        else:
            self._timer2 = self._timer2 + self._clock.get_time()

            # Repeat time 2 not reached
        if self._timer2 < self.repeat_time_2:
            return None

        self._timer2 = self._timer2 % self.repeat_time_2
        return pygame.event.Event(COMMAND_EVENT, {"command": self._pressed_command, "origin": self._pressed_event})

    @staticmethod
    def _dir_to_code(vector: (float, float)) -> str:
        x, y = vector
        press = 0.8  # Full press only
        if x <= -press:
            return "LEFT"
        if x >= press:
            return "RIGHT"
        if y >= press:
            return "UP"
        if y <= -press:
            return "DOWN"

    def _append_custom_event(self, command: str, event: pygame.event.Event, events: list):
        if command in REPEATABLE:
            if self._press(command, event) is True:
                events.append(pygame.event.Event(COMMAND_EVENT, {"command": command, "origin": event}))
        else:
            events.append(pygame.event.Event(COMMAND_EVENT, {"command": command, "origin": event}))

    def _apply_custom_events(self, events: list) -> list:
        mapped_events = []
        for e in events:
            match e.type:
                case pygame.KEYDOWN:
                    code = KBD_MAP.get(e.key)
                    if code is not None:
                        self._append_custom_event(code, e, mapped_events)
                    else:
                        mapped_events.append(e)
                case pygame.KEYUP:
                    self._release(e)

                case pygame.JOYBUTTONDOWN:
                    code = JOY_MAP.get(e.button)
                    if code is not None:
                        self._append_custom_event(code, e, mapped_events)
                    else:
                        mapped_events.append(e)
                case pygame.JOYBUTTONUP:
                    self._release(e)

                case pygame.JOYHATMOTION:
                    code = self._dir_to_code(e.value)
                    if code is not None:
                        self._append_custom_event(code, e, mapped_events)
                    else:
                        self._release(e)

                case pygame.JOYAXISMOTION:
                    code = None
                    if e.axis == pygame.CONTROLLER_AXIS_LEFTX:
                        code = self._dir_to_code([e.value, 0])
                        if code is None:
                            self._release(e)
                    elif e.axis == pygame.CONTROLLER_AXIS_LEFTY:
                        code = self._dir_to_code([0, -e.value])
                        if code is None:
                            self._release(e)
                    else:
                        mapped_events.append(e)
                    if code is not None:
                        self._append_custom_event(code, e, mapped_events)
                case _:
                    mapped_events.append(e)
        return mapped_events

    def update_controls(self) -> None:
        # Basic processing. Track release key
        events = []
        for e in pygame.event.get():
            match e.type:
                case pygame.JOYDEVICEADDED:
                    js = pygame.joystick.Joystick(e.device_index)
                    self.init_all_js()
                    print(f"Joystick added: {str(js.get_name())}")
                case pygame.JOYDEVICEREMOVED:
                    print(f"Joystick removed: {e.instance_id}")
                    self.init_all_js()
                case pygame.KEYUP:
                    self._release(e)
                case pygame.JOYBUTTONUP:  # instance_id, button
                    self._release(e)
            events.append(e)

        # Map to custom events
        self.events = self._apply_custom_events(events)

        # Apply repeated key
        repeat_event = self._get_repeated_key()
        if repeat_event is not None:
            self.events.append(repeat_event)

    def game_tick(self) -> None:
        self._clock.tick(30)  # limits FPS to 30

    def get_tick_time(self) -> float:
        return self._clock.get_time()  # Milliseconds
