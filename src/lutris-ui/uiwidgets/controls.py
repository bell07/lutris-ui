import pygame

from settings import Settings


# UI Controls proxy
class Controls:
    COMMAND_EVENT = pygame.event.custom_type()

    def __init__(self, repeatable_commands: tuple = None, keyboard_commands: dict = None,
                 joypad_keys_commands: dict = None):
        self.repeatable_commands = repeatable_commands or {}
        self.keyboard_commands = keyboard_commands or []
        self.joypad_keys_commands = joypad_keys_commands or []
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
        self._timer1 += self._clock.get_time()

        # Repeat time 1 not reached
        if self._timer1 < self.repeat_time_1 and self._timer2 is None:
            return None

        # Check for timer 2
        if self._timer2 is None:
            self._timer2 = 0
            return pygame.event.Event(Controls.COMMAND_EVENT,
                                      {"command": self._pressed_command, "origin": self._pressed_event})
        else:
            self._timer2 += self._clock.get_time()

            # Repeat time 2 not reached
        if self._timer2 < self.repeat_time_2:
            return None

        self._timer2 = self._timer2 % self.repeat_time_2
        return pygame.event.Event(Controls.COMMAND_EVENT,
                                  {"command": self._pressed_command, "origin": self._pressed_event})

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
        if command in self.repeatable_commands:
            if self._press(command, event) is True:
                events.append(pygame.event.Event(Controls.COMMAND_EVENT, {"command": command, "origin": event}))
        else:
            events.append(pygame.event.Event(Controls.COMMAND_EVENT, {"command": command, "origin": event}))

    def _apply_custom_events(self, events: list) -> list:
        mapped_events = []
        for e in events:
            match e.type:
                case pygame.KEYDOWN:
                    code = self.keyboard_commands.get(e.key)
                    if code is not None and (
                            e.mod & ~(pygame.KMOD_CAPS | pygame.KMOD_NUM | pygame.KMOD_MODE) == pygame.KMOD_NONE):
                        self._append_custom_event(code, e, mapped_events)
                    else:
                        mapped_events.append(e)
                case pygame.KEYUP:
                    self._release(e)

                case pygame.JOYBUTTONDOWN:
                    code = self.joypad_keys_commands.get(e.button)
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
