import time

import pygame

from settings import Settings


# UI Controls proxy
class Controls:
    COMMAND_EVENT = pygame.event.custom_type()

    def __init__(self, repeatable_commands: tuple = None, keyboard_commands: dict[int: str] = None,
                 joypad_keys_commands: dict[int: str] = None,
                 allowed_event_types: tuple = None):
        self.repeatable_commands = repeatable_commands or {}
        self.keyboard_commands = keyboard_commands or []
        self.joypad_keys_commands = joypad_keys_commands or []
        self.events = []
        settings = Settings("input")
        self.repeat_time_1 = settings.get("repeat_time_1", 500)  # ms
        self.repeat_time_2 = settings.get("repeat_time_2", 200)  # ms

        self._clock = pygame.time.Clock()
        self._timer1 = 0  # Timer 1 since key is pressed
        self._timer2 = None  # Timer 2 since key was processed last time
        self._pressed_command = None
        self._pressed_event = None
        self._last_axis = None
        self.allowed_event_types = allowed_event_types

        if allowed_event_types is not None:
            self.allowed_event_types += (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP,
                                         pygame.JOYAXISMOTION, pygame.JOYHATMOTION,
                                         Controls.COMMAND_EVENT,
                                         pygame.KEYDOWN, pygame.KEYUP,
                                         pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED)
        self.init_all_js()

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
            self._timer1 = time.time()
            self._timer2 = None
            return True  # Pressed first time

    def _release(self, release_event: pygame.event.Event = None) -> None:
        if self._pressed_event is None or release_event is None \
                or self._is_same(release_event, self._pressed_event):
            self._pressed_command = None
            self._pressed_event = None

    def _get_repeated_key(self) -> pygame.event.Event | None:
        # Nothing pressed
        if self._pressed_command is None:
            return None

        now = time.time()

        # Repeat time 1 not reached
        if (now - self._timer1) * 1000 < self.repeat_time_1 and self._timer2 is None:
            return None

        # Check for timer 2
        if self._timer2 is None:
            self._timer2 = now
            return pygame.event.Event(Controls.COMMAND_EVENT,
                                      {"command": self._pressed_command, "origin": self._pressed_event})

            # Repeat time 2 not reached
        if (now - self._timer2) * 1000 < self.repeat_time_2:
            return None

        self._timer2 = now
        return pygame.event.Event(Controls.COMMAND_EVENT,
                                  {"command": self._pressed_command, "origin": self._pressed_event})

    @staticmethod
    def _dir_to_code(vector: (float, float)) -> (str, int):
        x, y = vector
        press = 0.1
        command, value = None, 0

        if x <= -press:
            command, value = "LEFT", -x
        if x >= press:
            command, value = "RIGHT", x
        if y >= press:
            command, value = "UP", y
        if y <= -press:
            command, value = "DOWN", -y

        if value > 0.8:  # Pressed
            return command, value

        if value < 0.5:  # Released
            return "RELEASE", 0

        return None, 0  # Ignore, repeat allowed

    def _append_custom_event(self, command: str, event: pygame.event.Event, events: list):
        if any(e.type == Controls.COMMAND_EVENT for e in events):
            return  # Only 1 command in game step
        events.append(pygame.event.Event(Controls.COMMAND_EVENT, {"command": command, "origin": event}))
        if command in self.repeatable_commands:
            self._press(command, event)

    def _apply_custom_events(self, events: list) -> None:
        axis = self._last_axis
        axis_command = None
        axis_command_value = 0
        axis_command_event = None
        axis_released = False

        for e in events:
            match e.type:
                case pygame.KEYDOWN:
                    code = self.keyboard_commands.get(e.key)
                    if code is not None and (
                            e.mod & ~(pygame.KMOD_CAPS | pygame.KMOD_NUM | pygame.KMOD_MODE) == pygame.KMOD_NONE):
                        self._append_custom_event(code, e, events)

                case pygame.KEYUP:
                    self._release(e)

                case pygame.JOYBUTTONDOWN:
                    code = self.joypad_keys_commands.get(e.button)
                    if code is not None:
                        self._append_custom_event(code, e, events)
                case pygame.JOYBUTTONUP:
                    self._release(e)

                case pygame.JOYHATMOTION:
                    code, value = self._dir_to_code(e.value)
                    if code is not None and value == 1:
                        self._append_custom_event(code, e, events)
                    else:
                        self._release(e)

                case pygame.JOYAXISMOTION:
                    code = None
                    value = 0
                    if e.axis == pygame.CONTROLLER_AXIS_LEFTX:
                        code, value = self._dir_to_code([e.value, 0])
                    elif e.axis == pygame.CONTROLLER_AXIS_LEFTY:
                        code, value = self._dir_to_code([0, -e.value])
                    if code is not None:
                        if code == "RELEASE" and (axis is None or e.axis == axis):
                            axis_released = True
                        elif value > axis_command_value:
                            axis = e.axis
                            axis_command = code
                            axis_command_value = value
                            axis_command_event = e
                            axis_released = False

        if axis_released is True:
            self._release()
            self._last_axis = None
        elif axis_command is not None and self._last_axis != axis:
            self._last_axis = axis
            self._append_custom_event(axis_command, axis_command_event, events)

    def update_controls(self) -> None:
        self.events.clear()
        if self._pressed_command is None:
            wait_event = pygame.event.wait(timeout=5000)
            if wait_event.type != pygame.NOEVENT:
                self.events.append(wait_event)
        self.events += pygame.event.get()

        # Basic processing. Track release key
        if self.events:
            for e in self.events:
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

            # Map to custom events
            self._apply_custom_events(self.events)
        elif self.events:
            self.events.clear()

        # Apply repeated key
        repeat_event = self._get_repeated_key()
        if repeat_event is not None:
            if any(e.type == Controls.COMMAND_EVENT for e in self.events):
                return  # Only 1 command in game step
            self.events.append(repeat_event)

    def game_tick(self) -> None:
        self._clock.tick(30)  # limits FPS to 30

    def get_tick_time(self) -> float:
        return self._clock.get_time()  # Milliseconds
