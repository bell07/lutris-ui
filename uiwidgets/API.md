# Widgets-API

The Widgets API is intended to manage all inputs and outputs in pygame based application.

## Controls

The Goal of the Controls class is to unify the inputs into "Commands". The Class implements the "Repeat button" in
generic way, usable for joystick buttons too.
Basically the class is used in UiApp.run() method internally

### Class attributes

| Attribute              | Type                       | Reason                  | Value is set |
|------------------------|----------------------------|-------------------------|--------------|
| Controls.COMMAND_EVENT | pygame.event.custom_type() | Event type for commands | Constant     |

### Attributes

| Attribute            | Type                                                                  | Reason                                                          | Value is set               |
|----------------------|-----------------------------------------------------------------------|-----------------------------------------------------------------|----------------------------|
| repeatable_commands  | List of Commands                                                      | The commands in this list are automatically repeated            | Constructor parameter      |
| keyboard_commands    | Dictionary of pygame.K_* keys to application commands                 | If the key appears, the custom event is added into events table | Constructor parameter      |
| joypad_keys_commands | Dictionary of pygame.CONTROLLER_BUTTON_* keys to application commands | If the key appears, the custom event is added into events table | Constructor parameter      |
| events               | list of pygame.Event                                                  | Contain all events for current application step                 | Method "update_controls"   |
| repeat_time_1        | milliseconds                                                          | Time to repeat the command first time                           | Settings file, default 500 |
| repeat_time_2        | milliseconds                                                          | Time to repeat the command second and more times                | Settings file, default 200 |

### Methods

| Method                          | Reason                                                                                                                       |
|---------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| init_all_js() -> None           | The method is called automatically if any joypad is connected or removed. Does re-initialization of all connected joysticks. |
| update_controls() -> None       | Read pygame.event and enhance them by commands and repeats. Provides the Controls().events Attribute                         | 
| game_tick() -> None             | Use the same pygame.Clock() for application step delay. Hardcoded to tick(30)                                                |
| get_tick_time() -> Milliseconds | Get time since application was launched                                                                                      |

### How to Use:

```
    ctr = Controls(repeatable_commands=(...),
                  keyboard_commands={...},
                  joypad_keys_commands={...})
    app = LutrisUiApp(ctr)
    app.run()
``` 

Then use Controls.COMMAND_EVENT in your UiWidget().process_events() Method

## UiWidget

Base widget class. This widget does not have own surface and draw into parent surface directly.

### Attributes

| Attribute      | Type                  | Reason                                                                                                                                    | Value is set                                     |
|----------------|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|
| parent_widget  | Widget()              | The underlying widget, this widget draw into                                                                                              | Constructor parameter                            |
| _dyn_rect      | DynamicRect(**kwargs) | Internal usage to get dimensions. Mentioned at this place because additional UiWidget parameters are passed into this object constructor. | Constructor, set_pos(), set_size(), set_border() |
| is_visible     | bool                  | Default is true. If set, the widget is drawn                                                                                              | set_visible()                                    |
| is_interactive | bool                  | Default is true. If set, the widget get inputs with position (mouse, touchscreen)                                                         | set_interactive()                                |
| is_focus       | bool                  | Default is False. If set, The pointless inputs (keyboard, joystick) are passed to this widget                                             | set_focus()                                      |
| updated        | bool                  | Is set in draw() method if anything was drawn. Used to track depending updates                                                            | draw()                                           |
| widgets        | list of Widget()      | is None or contains all children widgets                                                                                                  | add_child(), called in new child constructor     |
| focus_child    | Widget()              | The child widget with focus                                                                                                               |                                                  |
| bg_color       | pygame.Color()        | If set, the widget is filled with color before draw                                                                                       | Constructor parameter                            |
| border_color   | pygame.Color()        | If set, the widget border is filled with color                                                                                            | Constructor parameter                            |

### Methods

| Method                                                                    | Reason                                                                                                                                                                                           |
|---------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| set_parent_surface(parent: UiWidget)                                      | Called once on init in constructor and should not be called again                                                                                                                                |
| get_root_widget()                                                         | Search parents recursuvely to get the root widget                                                                                                                                                |
| get_parent_surface() -> pygame.Surface                                    | Get the parent widget surface to draw into                                                                                                                                                       |
| get_parent_size() -> (int, int)                                           | Get the size of the parent surface. Uses parent_widget.get_size() with exception in UiApp()                                                                                                      |
| get_rect(with_borders: bool = False) -> pygame.Rect                       | Get the widget coordinates, inside or outside borders, calculated in DynamicRect                                                                                                                 |
| get_size(with_borders: bool = False) -> (int, int)                        | Just wrapper for get_rect().size                                                                                                                                                                 |
| set_pos(**kwargs)                                                         | Set position parameters in DynamicRect object                                                                                                                                                    |
| set_size(**kwargs)                                                        | Set sizing parameters in DynamicRect object                                                                                                                                                      |
| set_border(border_color: Color = None, **kwargs)                          | Set border color and border sizing in DynamicRect object                                                                                                                                         | 
| get_surface(with_borders: bool = True) -> Surface                         | Get the Widget surface. In UiWidget it is a parent sub-surface                                                                                                                                   |
| compose(surface: Surface) -> bool                                         | Empty - to be redefined. This method should contain all drawings to surface. Provided surface is from get_surface(with_borders=False) method. Return value should be False, if nothing was drawn |
| compose_borders() -> bool                                                 | Draw all 4 borders into get_surface(with_borders=True) surface. Return false if no borders drawn                                                                                                 |
| is_changed() -> bool                                                      | Internally used to track if widget should be redrawn                                                                                                                                             |
| is_child_changed() -> bool                                                | Internally used to track if child update changed the current widget                                                                                                                              |
| is_parent_changed() -> bool                                               | Internally used to track if widget should be redrawn because parent was redrawn. The method includes check for overlapping sibling widgets changes                                               |
| set_changed()                                                             | Mark widget as changed. Mark parents as "child is changed"                                                                                                                                       |
| set_child_changed()                                                       | Used from set_changed to set all parents recursively as "child is changed"                                                                                                                       |
| unset_changed()                                                           | Internally used. Reset all changing flags after all drawings are done. The updated attribute remains till next draw                                                                              |
| set_focus(focus: bool = True)                                             | Set focus for widget. If focus is set to true, all parents get the focus too. Other childs of the parent looses the focus                                                                        |
| set_interactive(interactive: bool = True)                                 | Set interactive for widget. If interactive is set to false, the widget loose the focus too                                                                                                       |
| set_visible(visible: bool = True)                                         | Set visibility for widget. If visible is set to false, the widget loose the focus too                                                                                                            |
| draw()                                                                    | Used internally from run() method. Check for changes and draw bg_color, compose() and child.draw() recursively.                                                                                  |
| add_child(widget: UiWidget)                                               | Used internally. Called in child's constructor.                                                                                                                                                  |
| remove_child(widget: UiWidget)                                            | Disable and remove the child widget                                                                                                                                                              |
| get_widget_collide_point(widget: UiWidget, pos: (int, int)) -> (int, int) | Check if given pos is inside the widget. Return relative position inside the widget. In case of pointed top or left borders the value is negative                                                |
| get_child_by_pos(pos: (int, int)) -> (UiWidget, (int, int))               | Check all visible childs for position. Search is in reverse order, to get the widget from top of the widget stack if widgets overlaps                                                            |
| process_events(events: list, pos: (int, int) = None)                      | Called from run() method to deliver events recursively. Can ber redefined to add own events handling. The super().process_events() needs to be called to deliver events to the childs            |
| process_tick(milliseconds: float)                                         | Is called each game step for own logic recursively.Can ber redefined to add own game step logic. The super().process_tick() needs to be called to trigger the children widgets logic             | 

## UiWidgetStatic

Enhanced UiWidget class by own surface handling. The widget draw into own surface and blit them to the parent. Utilizing
own surface requires less compose() actions and allow to set alpha in surface

### Attributes

| Attribute | Type  | Reason                           | Value is set          |
|-----------|-------|----------------------------------|-----------------------|
| alpha     | 0-255 | Is applied to the widget surface | Constructor parameter |

### Methods

| Method                                             | Reason                                                                                                      |
|----------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| get_surface(with_borders: bool = False) -> Surface | Get the Widget surface. The internal surface is scaled automatically if widget size is changed              |                                                                                                                     |
| set_alpha(alpha: int)                              | Set and apply the the alpha value                                                                           |
| draw()                                             | Same as UiWidget's draw(). compose() only if widget is_changed(). Otherwise just blit from internal surface |

## UiApp

UiApp enhances the UiWidget to be the root Widget, including window and application management. Therefore, the UiWidget
interface is valid for this class too.
At this point only the UiApp specific attributes and methods are mentioned.

### Attributes

| Attribute       | Type          | Reason                                                                               | Value is set          |
|-----------------|---------------|--------------------------------------------------------------------------------------|-----------------------|
| controls        | Controls()    | The run() method calls the methods of this object in right order                     | Constructor parameter | 
| size_w / size_h | float / float | Used in init_display_settings() to set the desired window size. 0 means maximum size | Constructor parameter |
| fullscreen      | bool          | Used in init_display_settings to set fullscreen                                      | Constructor parameter |
| noframe         | bool          | Used in init_display_settings to set noframe (borderless window)                     | Constructor parameter |
| exit_loop       | bool          | If set to true, the run() Method ends                                                |

### Methods

| Method                                               | Reason                                                                                               |
|------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| init_display_settings(reset: bool = False)           | Called on application init. Can be used to show window again after iconify. Used to toggle "noframe" |
| process_events(events: list, pos: (int, int) = None) | Handle for EXIT command, Window resize and get the first position for pointeable events              |
| draw()                                               | Draw all widgets recursively. pygame.display.flip() only if anything updated                         | 
| run()                                                | Main loop with update_controls(), process_tick(), process_events(), draw() and game_tick()           |

Other methods overrides the UiWidget definitions because this widget is root, means it does not have parent widget.

## UiWidgetTextblock

A Widget that contains any text with line breaks. The text can be centered inside the widget.

### Attributes

| Attribute       | Type           | Reason                                               | Value is set          |
|-----------------|----------------|------------------------------------------------------|-----------------------|
| text            | string         | Text to be shown                                     | Constructor parameter |
| text_color      | pygame.Color   | Color of the text                                    | Constructor parameter |
| text_font       | font.Font.Font | Used font                                            | Constructor parameter |
| text_centered_x | bool           | Set to true if thext should be centered horizontally | Constructor parameter |
| text_centered_y | bool           | Set to true if thext should be centered vertically   | Constructor parameter |

| Method                    | Reason                     |
|---------------------------|----------------------------|
| compose(surface: Surface) | Contain the implementation |

## UiWidgetViewportContainer

container widget that contain une UiWidgetViewport and 2x UiWidgetScrollbar's

### Attributes

| Attribute                   | Type                                              | Reason                      | Value is set          |
|-----------------------------|---------------------------------------------------|-----------------------------|-----------------------|
| viewport_widget             | UiWidgetViewport                                  | Embedded viewport           | set_viewport_widget() |
| vertical_scrollbar_widget   | UiWidgetsScrollbar(scrollbar_is_horizontal=False) | Vertical scrollbar widget   | hard-coded            |
| horizontal_scrollbar_widget | UiWidgetsScrollbar(scrollbar_is_horizontal=True)  | Horizontal scrollbar widget | hard-coded            |

### Methods

| Method                                        | Reason                                                                                 |
|-----------------------------------------------|----------------------------------------------------------------------------------------|
| set_viewport_widget(widget: UiWidgetViewport) | Set the viewport widget to the first place. Scrollbars always drawn above the viewport |

## UiWidgetViewport

UiWidgetViewport is a scrollable surface that can be bigger then the parent widget. It can be redefined to implement the
scrollable
area content. The Port can be assigned to UiWidgetViewportContainer using set_viewport_widget() to add scrollbars.

### Attributes

| Attribute                        | Type          | Reason                                                                                                             | Value is set        |
|----------------------------------|---------------|--------------------------------------------------------------------------------------------------------------------|---------------------|
| shift_x / shift_y                | float / float | Scrolling position. Initial is 0 / 0 that means the left / top corner is shown                                     | external assignment |
| viewport_width / viewport_height | float / float | Viewport size. Note, if viewport is smaller then parent widget, the viewport grows automatically to fill he parent | set_size()          |

### Methods

| Method                                                    | Reason                                                                                        |
|-----------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| set_size(w: int, h: int)                                  | Set size of viewport. If size is smaller then parent, the size is adjusted to fill the parent |
| get_surface(with_borders: bool = False) -> pygame.Surface | Get the viewport surface including invisilbe area parts                                       |
| adjust_shift()                                            | Check if remaining area is fully visible after shift. scroll back if right/bottom is reached  |  
| draw()                                                    | draw childs and blit the visible area into parent surface                                     |
| process_events(events: list, pos: (int, int) = None)      | Handle touch drag for scrolling. do not pass events to childs if scrolling was happens        |

## UiWidgetsScrollbar

Scrollbar is implemented for usage in UiWidgetViewportContainer

### Attributes

| Attribute               | Type         | Reason                                                                                      | Value is set                          |
|-------------------------|--------------|---------------------------------------------------------------------------------------------|---------------------------------------|
| scrollbar_is_horizontal | bool         | Is horizontal (=True) or vertical (=False) scrollbar                                        | Constructor parameter                 |
| scrollbar_width         | float        | The bar width                                                                               | Constructor parameter, default 20     |
| scrollbar_color         | pygame.Color | The bar color                                                                               | Constructor parameter, default is red |
| current_value           | float        | Current scrolling value. Between 0 and (max_value - bar_value).                             | external assignment                   |
| bar_value               | float        | The scrollbar size. For UiWidgetViewport the value is proportionally to smaller parent size | external assignment                   |
| max_value               | float        | The maximum value. For UiWidgetViewport the value is proportionally to viewport size        | external assignment                   |

### Methods

| Method                                               | Reason                                                                               |
|------------------------------------------------------|--------------------------------------------------------------------------------------|
| adjust_scrollbar_by_viewport()                       | Adjust scrollbar attributes from parent_widget.viewport_widget size and shift values | 
| draw()                                               | if viewport_widget was updated, call adjust_scrollbar_by_viewport() before draw      |
| compose(surface: pygame.Surface) -> bool             | Compose the bar into surface                                                         |
| process_events(events: list, pos: (int, int) = None) | Handle scroll actions if the scrollbar is drawn using mouse or touchscreen           |

# Advanced

## DynamicRect

DynamicRect is used in all UiWidget's to handle the widget size. The class should nt be used separately.
All DynamicRect constructor parameters can be given to UiWidget constructor and set_pos(), set_size(), set_border()
methods.

### Dynamic Types

> DynamicTypes.TYPE_PIXEL

For position the value is pixel count from top or left site.
For size, it is the widget width / height including borders.
This type is default, if nothing given.

> DynamicTypes.TYPE_PIXEL_REVERSE

For position the value is pixel count from bottom or right site.
For size, it is the (reserved) size right of bottom the widget that should remain
This type is default, if nothing given.

> DynamicTypes.TYPE_PERCENT

Values relative to parent.
pos=50 means the top or left position is in the middle
size=50 means the size is half of the space between left or top position to the right position is

> DynamicTypes.TYPE_CENTER

Only for position. The value will be ignored and position calculated based on widget and root sizes

### Attributes

| Attribute                              | Type          | Reason                                                                                          | Value is set |
|----------------------------------------|---------------|-------------------------------------------------------------------------------------------------|--------------|
| parent_w / parent_h                    | float / float | Parent widget size. The DynamicRect track if the child is inside parent                         |              |
| pos_x_type / pos_y_type                | Dynamic Type  | Type of pos_x / pos_y values. See dynamic types                                                 |              |
| pos_x / pos_y                          | Size value    | The position value according dynamic type                                                       |              |
| size_x_type / size_y_type              | Dynamic Type  | Type of pos_x / pos_y values. See dynamic types                                                 |              |
| size_x / size_y                        | Size value    | The size value according dynamic type. If no size is given, default value is TYPE_PERCENT / 100 |              |
| border_top, border_bottom, border_left | Size value    | The border width on the sizes. In addition border_all is implemented that set all sites         |              |
| changed                                | bool          | Track changes. Calculation is cached internally. This attribute is set to trigger recalculation |              |

### Methods

| Method                                                                                                                                             | Reason                                                                                      |
|----------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| set_parent_size(parent_w: float = None, parent_h: float = None)                                                                                    | Set parent size from values                                                                 |
| set_parent_size_by_surface(parent_surface: Surface)                                                                                                | Set parent size from parent surface                                                         |
| set_pos(pos_x_type, pos_x: float = None, pos_y_type, pos_y: float = None)                                                                          | Change position                                                                             |
| set_size(size_w_type=None, size_w=None, size_h_type=None, size_h=None)                                                                             | Change size                                                                                 |
| set_border(border_all: float = None, border_top: float = None, border_bottom: float = None, border_left: float = None, border_right: float = None) | Set borders. "border_all" change all not specified borders                                  |
| get_size(with_borders: bool = False) -> (int, int)                                                                                                 | Get current size, with or without borders                                                   |
| get_rect(with_borders: bool = False) -> pygame.Rect                                                                                                | Get current size and position as pygame.Rect This method contain the main DynamicRect magic |

