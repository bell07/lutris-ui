from __future__ import annotations

from time import time

from pygame import constants, event, joystick
from pygame.time import Clock
from settings import Settings


# UI Controls proxy
class Controls:
    COMMAND_EVENT = event.custom_type()

    def __init__(
        self,
        repeatable_commands: list[str] | None = None,
        keyboard_commands: dict[int, str] | None = None,
        joypad_keys_commands: dict[int, str] | None = None,
        allowed_event_types: list[int] | None = None,
    ):
        self.repeatable_commands: list[str] = repeatable_commands or []
        self.keyboard_commands: dict[int, str] = keyboard_commands or {}
        self.joypad_keys_commands: dict[int, str] = joypad_keys_commands or {}
        self.events: list[event.Event] = []
        settings = Settings("input")
        self.repeat_time_1: float = settings.get("repeat_time_1", 500)  # ms
        self.repeat_time_2: float = settings.get("repeat_time_2", 200)  # ms

        self._clock = Clock()
        self._timer1: float = 0  # Timer 1 since key is pressed
        self._timer2: float | None = None  # Timer 2 since key was processed last time
        self._pressed_command: str | None = None
        self._pressed_event: event.Event | None = None
        self._last_axis = None
        self.allowed_event_types: list[int] | None = allowed_event_types

        if self.allowed_event_types:
            self.allowed_event_types += [
                constants.JOYBUTTONDOWN,
                constants.JOYBUTTONUP,
                constants.JOYAXISMOTION,
                constants.JOYHATMOTION,
                Controls.COMMAND_EVENT,
                constants.KEYDOWN,
                constants.KEYUP,
                constants.JOYDEVICEADDED,
                constants.JOYDEVICEREMOVED,
            ]

    @staticmethod
    def init_all_js() -> None:
        joystick.init()
        for i in range(joystick.get_count()):
            joystick.Joystick(i).init()

    @staticmethod
    def _is_same(event1: event.Event, event2: event.Event) -> bool:
        if event1.type != event2.type:  # Different types
            if (
                event1.type == constants.KEYDOWN and event2.type == constants.KEYUP
            ) or (event2.type == constants.KEYDOWN and event1.type == constants.KEYUP):
                return True

            if (
                event1.type == constants.JOYBUTTONDOWN
                and event2.type == constants.JOYBUTTONUP
            ) or (
                event2.type == constants.JOYBUTTONDOWN
                and event1.type == constants.JOYBUTTONUP
            ):
                return True

            return False
        if (
            event1.type == constants.JOYAXISMOTION and event1.axis != event2.axis
        ):  # Different axis
            return False

        return True

    def _press(self, command: str, event: event.Event) -> bool:
        if (
            self._pressed_command == command
            and self._pressed_event
            and self._is_same(self._pressed_event, event)
        ):
            return False
        else:
            self._pressed_command = command
            self._pressed_event = event
            self._timer1 = time()
            self._timer2 = None
            return True  # Pressed first time

    def _release(self, release_event: event.Event | None = None) -> None:
        if (
            self._pressed_event is None
            or release_event is None
            or self._is_same(release_event, self._pressed_event)
        ):
            self._pressed_command = None
            self._pressed_event = None

    def _get_repeated_key(self) -> event.Event | None:
        # Nothing pressed
        if self._pressed_command is None:
            return None

        now = time()

        # Repeat time 1 not reached
        if (now - self._timer1) * 1000 < self.repeat_time_1 and self._timer2 is None:
            return None

        # Check for timer 2
        if self._timer2 is None:
            self._timer2 = now
            return event.Event(
                Controls.COMMAND_EVENT,
                {"command": self._pressed_command, "origin": self._pressed_event},
            )

            # Repeat time 2 not reached
        if (now - self._timer2) * 1000 < self.repeat_time_2:
            return None

        self._timer2 = now
        return event.Event(
            Controls.COMMAND_EVENT,
            {"command": self._pressed_command, "origin": self._pressed_event},
        )

    @staticmethod
    def _dir_to_code(x: float, y: float) -> tuple[str | None, float]:
        press = 0.1
        command: str | None = None
        value: float = 0

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

    def _append_custom_event(
        self, command: str, custom_event: event.Event, events: list
    ):
        if any(e.type == Controls.COMMAND_EVENT for e in events):
            return  # Only 1 command in game step
        events.append(
            event.Event(
                Controls.COMMAND_EVENT, {"command": command, "origin": custom_event}
            )
        )
        if command in self.repeatable_commands:
            self._press(command, custom_event)

    def _apply_custom_events(self, events: list[event.Event]) -> None:
        axis = self._last_axis
        axis_command = None
        axis_command_value = 0
        axis_command_event: event.Event | None = None
        axis_released = False

        for e in events:
            match e.type:
                case constants.KEYDOWN:
                    code = self.keyboard_commands.get(e.key)
                    if code is not None and (
                        e.mod
                        & ~(
                            constants.KMOD_CAPS
                            | constants.KMOD_NUM
                            | constants.KMOD_MODE
                        )
                        == constants.KMOD_NONE
                    ):
                        self._append_custom_event(code, e, events)

                case constants.KEYUP:
                    self._release(e)

                case constants.JOYBUTTONDOWN:
                    code = self.joypad_keys_commands.get(e.button)
                    if code is not None:
                        self._append_custom_event(code, e, events)
                case constants.JOYBUTTONUP:
                    self._release(e)

                case constants.JOYHATMOTION:
                    code, value = self._dir_to_code(e.value[0], e.value[1])
                    if code is not None and value == 1:
                        self._append_custom_event(code, e, events)
                    else:
                        self._release(e)

                case constants.JOYAXISMOTION:
                    code = None
                    value = 0
                    if e.axis == constants.CONTROLLER_AXIS_LEFTX:
                        code, value = self._dir_to_code(e.value, 0)
                    elif e.axis == constants.CONTROLLER_AXIS_LEFTY:
                        code, value = self._dir_to_code(0, -e.value)
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
        elif (
            axis_command and axis_command_event is not None and self._last_axis != axis
        ):
            self._last_axis = axis
            self._append_custom_event(axis_command, axis_command_event, events)

    def init(self) -> None:
        self.init_all_js()

    def update_controls(self) -> None:
        self.events.clear()
        if self._pressed_command is None:
            wait_event = event.wait(timeout=5000)
            if wait_event.type != constants.NOEVENT:
                self.events.append(wait_event)
        self.events += event.get()

        # Basic processing. Track release key
        if self.events:
            for e in self.events:
                match e.type:
                    case constants.JOYDEVICEADDED:
                        js = joystick.Joystick(e.device_index)
                        self.init_all_js()
                        print(f"Joystick added: {str(js.get_name())}")
                    case constants.JOYDEVICEREMOVED:
                        print(f"Joystick removed: {e.instance_id}")
                        self.init_all_js()
                    case constants.KEYUP:
                        self._release(e)
                    case constants.JOYBUTTONUP:  # instance_id, button
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
