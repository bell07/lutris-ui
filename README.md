# Lutris-ui

Simple [pygame](https://www.pygame.org) based Lutris frontend.

Main goal is to launch Lutris games using joypad or touchscreen on portable gaming devices.
Using SDL2 based pygame library the frontend works on Xorg and on Wayland.
Lutris-UI is written in Python, the same scripting language as Lutris.

License: [GPL-v3](LICENSE.txt) - Same as Lutris

Project status: "Works-for-me". No warranty it does work for you. But any contribution is welcome


![Screnshot](screenshots/lutris%20and%20lutris-ui%20screenshot.png "Screenshot")
Left site is the Lutris window, right site is the Lutris-UI window.

## Dependencies

| Dependency | Reason                   | 
|------------|--------------------------|
| Python 3   | The interpreter          |
| Pygame 2.6 | Main UI library          |
| lutris     | Games manager and runner | 
| psutil     | Track running game       |
| pyxdg      | Get the config file path |

## Configuration

The repository provides [config.ini.example](config.ini.example) that can be placed to
XDG path `~/.config/lutris-ui/config.ini` and adjusted for your needs.
In short: you can set

- **game_widget**: game widget/tile size and distance
- **gamelist**: games order
- **play**: enable "hide on launch"
- **input**: Repeat times for arrow buttons
- **window**: Fullscreen, borderless window (noframe), or window size

## Usage

The launcher can be controlled by Keyboard, Joypad, Mouse or Touchscreen.

<details>
  <summary>Show all Controls</summary>

### Keyboard

| Key               | Action                                         |
|-------------------|------------------------------------------------|
| arrow keys        | change selection left / right / above / bellow |
| Enter             | Run game / Cancel running game                 |
| Left-ALT + Enter  | Toggle Fullscreen                              |
| Right-ALT + Enter | Toggle Borderless-Window-Fullscreen            |
| Escape            | Exit Lutris-UI                                 |
| K                 | Reload games                                   |

### Joystick

| Key                | Action                                         |
|--------------------|------------------------------------------------|
| D-Pad              | change selection left / right / above / bellow |
| Left Joystick move | change selection left / right / above / bellow |
| A                  | Run game / Cancel running game                 |
| Start              | Run game / Cancel running game                 |

### Mouse

| Mouse action                  | Action              |
|-------------------------------|---------------------|
| Left click to tile            | Run game            |
| Left click to "Cancel" button | Cancel running game | 
| Right / Middle click to tile  | Select game         |
| Wheel                         | Scroll              |

### Touchscreen

| Touchscreen action     | Action                                |
|------------------------|---------------------------------------|
| Tap game               | Select game. If selected,run the game | 
| Tap to "Cancel" button | Cancel running game                   |
| Drag vertical          | Scroll                                |

</details>

## For developers

For Lutris-UI I wrote a new [Widgets API](uiwidgets/API.md) with intention to release it separately later.
I know, they are some other pygame based API already. This Widget-API allow relative coordinates,
so window resizing is handled properly from beginning.
