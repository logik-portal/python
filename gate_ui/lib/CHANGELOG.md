# PyFlame Library Changelog

All notable changes to this project will be documented in this file.
 
https://logik-portal.com/pyflame

## v5.6.0 [11.23.26]

### Added

- **PyFlameCheckBox**
    - New check box widget: a small box with text beside it. It looks the same as the check boxes
      in a checkable `PyFlameTreeWidget`.
    - Arguments:
        - `text` (str): text shown beside the box. (Default: `''`)
        - `checked` (bool): whether the box starts checked. (Default: `False`)
        - `connect` (callable | None): function to call when the user clicks the check box.
          (Default: `None`)
        - `enabled` (bool): whether the check box can be clicked. (Default: `True`)
        - `width` (int | None): width of the widget. (Default: `None`)
        - `height` (int | None): height of the widget. (Default: `None`)
        - `tooltip` (str | None): tooltip text. (Default: `None`)
        - `tooltip_delay` (int): seconds before the tooltip shows. (Default: `3`)
        - `tooltip_duration` (int): seconds the tooltip stays up. (Default: `5`)
    - Every argument except `connect` is also a property that can be read and set.
      `connect_callback()` connects a function later.
    - The connected function is only called when the user clicks the check box. Setting `checked`
      from code does not call it.

- **PyFlameCheckBoxGroup**
    - New class that groups `PyFlameCheckBox` widgets and limits how many of them the user can have
      checked. More than one can be checked at a time.
    - Arguments:
        - `check_box_group` (list): the `PyFlameCheckBox` widgets in the group.
        - `min_checked` (int): fewest boxes that can be checked. `0` for no minimum. (Default: `1`)
        - `max_checked` (int | None): most boxes that can be checked. `None` for no maximum.
          (Default: `None`)
        - `connect` (callable | None): function to call, with no arguments, after the user changes
          a check box in the group. (Default: `None`)
    - Properties: `check_box_group`, `min_checked`, `max_checked`, `connect_callback`, and the
      read-only `checked_check_boxes` (the checked widgets) and `checked_text` (their text).
    - A click that would leave fewer than `min_checked` or more than `max_checked` boxes checked is
      ignored: the box doesn't change and no connected function is called.
    - The limits only apply to the user. The group never changes a check box itself, and code can
      still set any box's `checked`, so the script sets the starting state.
    - Keep a reference to the group, such as `self.check_box_group = PyFlameCheckBoxGroup(...)`.
      If the group is deleted, the limits stop working.

- **PyFlameHelpWindow**
    - New window class that shows a Markdown file, such as a script's README.md, fully rendered:
      headings, bold text, `code`, lists, tables and images. Images wider than the text are scaled
      down to fit. Links to a heading in the same file scroll to it; http, https and mailto links
      open in the web browser.
    - Arguments:
        - `readme_path` (str): path of the Markdown file to show. Image paths in it are relative to
          the folder the file is in.
        - `script_url` (str | None): web address of the script on the Logik Portal. (Default: `None`)
        - `title` (str): window title. (Default: `'Help'`)
        - `parent` (PyFlameWindow | None): parent window. (Default: `None`)
    - When `script_url` is given, a **Logik Portal** button at the bottom left opens it in the web
      browser. The button only appears once a check in the background (2 second timeout) has
      reached the web address. Without a connection it never appears, and opening the window never
      waits for the check.
    - The window is not modal, so it can stay open beside other windows. It stays open without a
      reference being kept to it. `is_open()`, `show()` and `close()` check it, bring it to the
      front and close it.
    - If the Markdown file can't be read, an error message is shown instead of the window.

### Updates

- **Widgets**
    - `PyFlameToolTip`
        - **Fixed**
            - Tooltip text with more than one line (lines separated with `\n`) was cut off after the
              first line. The tooltip now grows to fit all of its lines.
            - Removed a leftover debug print (`Duration: 5000`) that was printed every time a tooltip
              was shown.
            - A `RuntimeError: Internal C++ object (QTimer) already deleted` message was printed
              when Python exits.
            - Its docstring said the `delay` and `duration` getters return seconds. They return
              milliseconds (used by the tooltip's own timers). The docstring now says so. Nothing
              else changed.
        - **New Behavior**
            - Tooltip text is now word wrapped. Text wider than about 60 characters wraps onto more
              lines. Shorter text stays on one line. Use `\n` to force a line break.
    - `PyFlameTreeWidget`
        - **Fixed**
            - After `elide_text` was `True`, setting it to `False` did not bring back the `...` on long
              text. It now does.
            - Setting `connect_callback` or `update_connect_callback` again left the old function
              connected, so both were called, and setting `None` did not remove it. Only the latest
              function is now called, and `None` removes it. Trees that set these once, when created,
              are unchanged.
            - Its docstring said `fill_tree_dict`'s `editable` sets whether the items can be edited.
              It has no effect: child items are always editable and top-level items follow
              `top_level_editable`. It now says so, and how to stop editing
              (`setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)`). Docstring only.
        - **Updated Stylesheet**
            - Checkbox styling added. Only applied when `checkable` is `True`.
        - **New Argument**
            - `checkable`
                - When set to `True`, every item in the tree shows a checkbox in the first column. Items
                  start checked. Checking a parent item does not change its children.
                  (Default: `False`)
            - `check_connect`
                - Function to call when a checkbox is checked or unchecked, by the user or through the
                  methods below. Not called while the tree is being filled.
                  (Default: `None`)
            - `draggable`
                - When set to `True`, items can be dragged out of the tree onto another widget. Drag
                  only: the dragged item is copied, never removed from the tree, and the tree does
                  not accept drops. An item can be dragged if it can be selected, so with
                  `top_level_selectable=False` the top-level items cannot be dragged.
                  (Default: `False`)
            - `drag_end_connect`
                - Function to call when a drag that started in the tree has ended, whether it was
                  dropped or cancelled. Only used when `draggable` is `True`.
                  (Default: `None`)
            - `context_menu`
                - Right-click menu for the tree: a dict of menu item text mapped to the function to
                  call (with no arguments) when that item is chosen. Items are shown in dict order.
                  A right-click on an item that can be selected selects it first. If `None` or
                  empty, there is no menu and a right-click works as before.
                  (Default: `None`)
        - **New Property**
            - `checkable`
                - Get or set whether items show a checkbox.
            - `check_connect_callback`
                - Get or set the function called when a checkbox changes.
            - `draggable`
                - Get or set whether items can be dragged out of the tree.
            - `drag_end_connect_callback`
                - Get or set the function called when a drag has ended.
            - `context_menu`
                - Get or set the right-click menu. Set to `None` to remove it.
            - `checked_items`
                - Read-only. List of all checked items, in tree order.
            - `unchecked_items`
                - Read-only. List of all unchecked items, in tree order.
        - **New Method**
            - `set_item_checked(item, checked)`
                - Check or uncheck an item.
            - `is_item_checked(item)`
                - Return `True` if the item is checked.
            - `check_all()`
                - Check every item in the tree.
            - `uncheck_all()`
                - Uncheck every item in the tree.
        - **Updated Method**
            - `add_item_with_columns`
                - New argument `checked`. Sets whether the new item starts checked. Only used when
                  `checkable` is `True`. (Default: `True`)
    - `PyFlameListWidget`
        - **Fixed**
            - The `add_items` type errors named the argument twice
              (`PyFlameListWidget.add_items: items: Expected 'items' ...`). They now read
              `PyFlameListWidget.add_items: Expected 'items' ...`.
        - **New Argument**
            - `draggable`
                - When set to `True`, items can be dragged out of the list onto another widget. Drag
                  only: the dragged items are copied, never removed from the list, and the list does
                  not accept drops.
                  (Default: `False`)
            - `drag_end_connect`
                - Function to call when a drag that started in the list has ended, whether it was
                  dropped or cancelled. Only used when `draggable` is `True`.
                  (Default: `None`)
            - `context_menu`
                - Right-click menu for the list: a dict of menu item text mapped to the function to
                  call (with no arguments) when that item is chosen. Items are shown in dict order.
                  A right-click on an item that can be selected selects it first. If `None` or
                  empty, there is no menu and a right-click works as before.
                  (Default: `None`)
        - **New Property**
            - `draggable`
                - Get or set whether items can be dragged out of the list.
            - `drag_end_connect_callback`
                - Get or set the function called when a drag has ended.
            - `context_menu`
                - Get or set the right-click menu. Set to `None` to remove it.
    - `PyFlameHorizontalLine` / `PyFlameVerticalLine`
        - **Fixed**
            - Setting `color` after the line was created changed nothing on screen. The line now
              changes color. Setting it when the widget is created works as before.
    - `PyFlameMenu`
        - **New Property**
            - `connect_callback`
                - Get or set the function called when a menu item is selected. `None` disconnects it.
                  Setting it does not change the menu text or the menu options.
        - **Fixed**
            - Setting `align` or `menu_indicator` after the menu was created changed nothing on screen.
              The menu now updates. Setting it when the widget is created works as before.
            - Reading the `tooltip` property raised an `AttributeError`. It now returns the tooltip
              text.
            - The function given to `connect` stopped being called after the menu was rebuilt.
              `update_menu()` without `connect` left the menu with no function, and setting
              `menu_options` or calling `refresh_menu()` after `update_menu(connect=...)` went back
              to the constructor's function (or none). The function from the constructor, or from the
              latest `update_menu(connect=...)`, now stays connected through every rebuild until a new
              one is given. `update_menu()` without `connect` keeps the current function (it no
              longer disconnects it). It is still called once per pick.
            - The docstrings didn't say that when the menu options are set and there are two or
              more, menu text that is not one of the options (a placeholder or an old saved choice)
              is replaced by the first option, and that with zero or one option the menu shows that
              option (or is empty). The class, `text`, `menu_options` and `update_menu()` docstrings
              now say so. This is how the menu already worked; nothing changed.
    - `PyFlameColorMenu`
        - **Fixed**
            - Setting `menu_indicator` after the menu was created changed nothing on screen, and setting
              `color` changed the text but left the old color swatch. Both now update. A `color` that is
              not one of the color options still only changes the text.
            - Setting `tooltip_delay` to something that is not a whole number gave an error that
              named `tooltip` instead of `tooltip_delay`. It now names `tooltip_delay`.
            - Setting `enabled` to something that is not a bool gave an error that named
              `PyFlameMenu` instead of `PyFlameColorMenu`. It now names `PyFlameColorMenu`.
            - The error for a color that is not four floats between 0 and 1 said "three floats".
              It now says "four floats". Message only: the same colors are accepted.
    - `PyFlameSlider`
        - **Fixed**
            - Passing a function to `connect` (or to the `connect_callback()` method) raised an `AttributeError`. The
              function is now called, with no arguments, every time the slider value changes.
            - Calculator: `*` and `/` with a number of more than one digit only used the last digit:
              `*25` multiplied by 5, and `/10` set the slider to 0 or its minimum. The whole number is
              now used.
            - Calculator: an unfinished or invalid entry (`5+`, `1/0`, `1..2`, `=` and so on) set the
              slider to 0 or its minimum. The slider value is now left as it was and the calculator
              stays open with the entry unchanged, so it can be corrected.
            - Calculator: numbers with leading zeros inside a calculation (`5+010`) are now read as
              decimal numbers. Before, the whole calculation gave 0.
            - Calculator: calculations starting with `-` (`-50+10`, `-5*2`), or with `0` (`0-5`), gave
              wrong results. They are now worked out as written. `*-1` now negates the value.
            - Calculator: after Add or Sub, numbers typed on the keyboard were added to the end of the
              shown number and then ignored when Return was pressed. Typing now starts a new entry,
              the same as the calculator's number buttons, and Return applies it.
            - Calculator: pressing Shift, Ctrl or an arrow key after Add or Sub cleared the entry.
            - Calculator: the slider stayed highlighted when the calculator was closed with Enter
              after Add or Sub, or by clicking outside it.
            - Calculator: the `+/-` button raised a `ValueError` when the entry held a calculation
              (`5+3`) or just `-`. It now negates the result of the calculation, and does nothing if
              the entry isn't a valid calculation.
            - Calculator: Add or Sub with `0.0` or `.0` added or subtracted 1. Adding or subtracting
              zero now changes nothing.
            - Calculator: powers (`2**3`) set the slider to 1. They are now treated as an invalid
              entry.
            - Calculator: the `=` button showed `0` for an invalid entry, or `1` for a power. It now
              leaves the entry as it is.
            - Calculator: pressing Return in the entry applied the entry twice.
            - Calculator: after Add or Sub with zero (or an empty entry), Enter set the slider to 0.
              Enter now just closes the calculator, the same as after any other Add or Sub.
            - Calculator: after Add or Sub, editing the shown number with Backspace or Delete was
              ignored when Return was pressed. The edited number is now applied, the same as a typed
              entry.
            - The calculator raised a `TypeError` when the slider was not inside a `PyFlameWindow`.
            - Sliders with a decimal range (for example 0.1 to 2.0): the small bar under the number
              only moved in whole numbers, so it jumped between a few places. It now moves smoothly
              from one end to the other. Sliders with a whole number range are unchanged.
            - The small bar under the number did not follow `min_value` or `max_value` when they
              were set after the slider was created. It now updates when either one is set.
    - `PyFlameProgressBarWidget`
        - **Fixed**
            - Setting `bar_color` after the bar was created changed nothing on screen. The bar now
              changes color. Setting it when the widget is created works as before.
            - Reading the `processing_task` property raised an `AttributeError`. It now returns the
              value that was set.
    - `PyFlameButtonGroup`
        - **Fixed**
            - Reading the `set_exclusive` property raised an `AttributeError`. It now returns whether
              the button group is exclusive.
    - `PyFlameTable`
        - **Fixed**
            - The Rename Column Header and Rename Selected Cells windows were opened without the
              table's window as their parent, so they did not block that window or stay above it.
              When the table was in a window created with `modal=True`, they could not be used at
              all until that window was closed. They now use the table's window as their parent
              when it is a `PyFlameWindow`.
            - `save_csv_file()` saved the old text of a cell that was still being edited (for example
              when a Save button was clicked before pressing Return), and left the cell's editor open.
              The edited text is now put into the table and the editor closed before saving.
            - Right-click Delete Row / Delete Column deleted the selected rows or columns, not the
              one that was right-clicked, and did nothing when nothing was selected. They now delete
              the right-clicked row or column. If it is one of the selected rows or columns, all of
              the selected ones are deleted. Right-clicking past the last row or column still
              deletes the selection.
            - A CSV file with data rows longer than the header row (for example a comma at the end of
              each data line) gave the extra columns a number as their header. Saving wrote that number
              as a header name, and double-clicking the header raised an error. These columns now get
              an empty header, which is saved as an empty field and can be renamed.
            - Rename Column Header in the right-click menu, and double-clicking, raised an error when
              used in the empty header area past the last column. The menu no longer offers it there,
              and double-clicking that area does nothing.
            - Loading a CSV file and saving it again without changes no longer changes the file in
              these ways: a UTF-8 BOM at the start of the file was dropped (Excel may then show
              accented letters wrongly), an empty file was saved as an empty line, and blank lines
              were saved as rows of commas. The BOM is now saved again, an empty file stays empty, and
              a blank line is saved as a blank line as long as no text is typed into its row (except
              in a file whose first line is blank, where they are saved as before). A blank line still
              shows as an empty row, and rows added with Add Row are saved as before.
            - In a CSV file starting with a UTF-8 BOM, a first header in quotes (for example
              `"Name, Full"`) was read with its quotes and split at the comma. It is now read the same
              as in a file without a BOM.
            - The right-click menus of the row and column headers were kept in memory until the
              table's window was closed, one more each time a menu was opened. Each menu is now
              freed after it closes.
            - Setting `tooltip` to `None` did not remove the tooltip. It now removes it.
            - `load_csv('')` set `csv_file_path` to `''` while the table kept the data from the
              loaded file. An empty path now leaves `csv_file_path` as it was. `load_csv(None)` is
              unchanged.
            - The docstring said `csv_file_path` can be set, but it is read only (it is set by
              `load_csv()`), and its `tooltip_delay` example used `0.5`, which raises an error
              because the delay is a whole number of seconds. Both are corrected.
        - **New Behavior**
            - A CSV file that isn't saved as UTF-8 (for example "CSV (Comma delimited)" from Excel)
              used to load with unreadable characters, and saving it then replaced them in the file
              for good. Such a file is now not loaded: an error message says to save it again as
              "CSV UTF-8", and the table, its headers and `csv_file_path` stay as they were. Until
              that file or another file is loaded, `save_csv_file()` won't save over it and shows an
              error message instead. UTF-8 files, with or without a BOM, load as before.
    - `PyFlameTabWidget`
        - **Fixed**
            - Setting `tab_label_width` or `tab_label_height` after the tab widget was created changed
              nothing on screen. The tab labels now resize. The value is used as given (it is not
              scaled, unlike the constructor arguments).
            - `enabled=False` didn't disable anything: the value was stored but never applied. The tab
              pages (and every widget on them) are now disabled, including tabs added later with
              `add_tab`. The tab bar stays enabled, so tabs can still be switched. With the default
              `enabled=True` nothing changes.
    - `PyFlameGridLayout`
        - **Fixed**
            - Its docstring said a wrong argument type raises a `TypeError`. Nothing is checked: the
              grid values are plain attributes, changing them after the layout is created doesn't change
              the grid, and widgets are added with Qt's own `addWidget`. It now says so. Docstring only.
    - `PyFlameHBoxLayout` / `PyFlameVBoxLayout`
        - **Fixed**
            - `PyFlameHBoxLayout.addSpacing` errors named `setSpacing`, and `PyFlameVBoxLayout.setSpacing`
              errors named `setSpacing` as the argument (`Expected 'setSpacing' to be int`). They now
              name the right method and the `spacing` argument. The same values are accepted.
    - `PyFlameLabel`
        - **Fixed**
            - `Style.BORDER` drew the border in the wrong color (black, or the palette color on
              older Qt): the stylesheet said `rgbrgb(64, 64, 64)`. The border is now
              `rgb(64, 64, 64)` as documented. Other styles are unchanged.
    - `Color`
        - **Fixed**
            - `Color.UNDERLINE` was `rgb(40, 40, 40, 1)`, an `rgb` value with an alpha part. Used in a
              stylesheet it drew black, or nothing on older Qt. It is now `rgb(40, 40, 40)`, the same
              as `Color.TEXT_UNDERLINE`. Nothing in the library uses it by default.
    - `PyFlameTextBrowser`
        - **Fixed**
            - Its docstring said `TextStyle.EDITABLE` gives editable text and `TextStyle.UNSELECTABLE`
              unselectable text. `text_style` only sets the look: the text browser is always read only
              and its text can always be selected. `TextStyle.READ_ONLY_SELECTABLE` is accepted but
              doesn't change the look. It now says so. Docstring only.
    - `PyFlameTextEdit`
        - **Fixed**
            - With `text_type=TextType.MARKDOWN`, letters with only an upright stroke (i, l) were
              missing from headers. The light weight used for Markdown text is drawn with the
              Montserrat Thin face, which loses those strokes at header sizes. Headers are now set
              in the regular weight. Body text is unchanged.
    - `PyFlameTextEdit` / `PyFlameTextBrowser`
        - **Fixed**
            - With `text_type=TextType.MARKDOWN`, everything after some raw HTML in the Markdown was
              missing: after a `<br>`, `<hr>` or `<img ...>` that isn't self-closed, a `<Token>`
              written as plain text (for example `<ShotName>`), a closing tag with no opening tag,
              or a comment with a tag in it. Qt's Markdown reader waits for every tag it counted as
              opened to be closed, and drops the rest of the text when one never is. The Markdown
              is now checked before it is set, and when text would be lost a fixed copy is set
              instead: those void elements are made self-closing, the other tags are shown as
              written, and those comments are removed.
                - Markdown that already showed in full is set exactly as before. So is Markdown
                  whose only problem is an unclosed tag at the very end with nothing after it.
                - The fixed copy is only used if all of it is shown, what was shown before is still
                  shown in the same order, and it has no fewer links, images or tables. Otherwise
                  the Markdown is set as it was.
                - Code is left as it is where it can be told apart. In Markdown that was losing
                  text, a tag inside code can now and then show as `&lt;`, and an unclosed tag at
                  the end can show as written.
                - Markdown over 1,000,000 characters, with more than 5000 tags or tags nested more
                  than 200 deep, or that takes longer than about a quarter of a second to check and
                  fix, is set as it was.
                - The `text` getter is unchanged.
    - `PyFlameEntry` / `PyFlameEntryBrowser`
        - **Fixed**
            - `placeholder_text` could not be cleared: setting it to `''` or `None` kept the old
              placeholder on screen. It is now removed. Setting a text works as before.
    - `PyFlameEntry`
        - **Fixed**
            - Setting `read_only` after the entry was created made it read only (or editable) but kept
              the old look. The entry now switches to the matching look.
            - Tooltips never appeared. The tooltip delay and duration were converted to milliseconds
              twice, so the default 3 second delay became 50 minutes. Tooltips now appear after
              `tooltip_delay` seconds and stay for `tooltip_duration` seconds, like other widgets.
            - Holding Alt over an entry that has a tooltip showed the full text label and the
              tooltip at the same spot. While the Alt full text label is showing, the tooltip is now
              hidden and doesn't pop up. After Alt is released, the tooltip shows again the next
              time the mouse enters the entry. Entries without a tooltip are unchanged.
            - Setting `tooltip` to `None` did not remove the tooltip. It now removes it.
    - `PyFlameButton` / `PyFlameEntry` / `PyFlameEntryBrowser` / `PyFlameListWidget` /
      `PyFlamePushButton` / `PyFlameMenu` / `PyFlameColorMenu` / `PyFlameTokenMenu` /
      `PyFlameSlider` / `PyFlameTable` / `PyFlameTextEdit` / `PyFlameTextBrowser` /
      `PyFlameTreeWidget`
        - **Fixed**
            - Reading `tooltip_delay` or `tooltip_duration` gave milliseconds, while setting them
              takes seconds, so `widget.tooltip_delay = widget.tooltip_delay` turned a 3 second
              delay into 50 minutes. They now give back the seconds that were set (a whole number,
              for example `3`).
            - The `tooltip_delay` docstring examples used `0.5`, which raises an error because the
              delay is a whole number of seconds. The examples now use `1` (the `PyFlameTable`
              example is listed under `PyFlameTable` above).
            - The `tooltip_delay` and `tooltip_duration` docstring examples in `PyFlameEntry`,
              `PyFlameEntryBrowser`, `PyFlameColorMenu`, `PyFlameTokenMenu` and `PyFlameTextEdit`
              used another widget's variable name (`button.`, `menu.`, `text_browser.`). They now
              use the class's own name (`entry.`, `color_menu.`, `token_push_button.`,
              `text_edit.`).
    - `PyFlameButton` / `PyFlameEntryBrowser` / `PyFlameListWidget` / `PyFlamePushButton` /
      `PyFlameMenu` / `PyFlameColorMenu` / `PyFlameTokenMenu` / `PyFlameSlider` /
      `PyFlameTextEdit` / `PyFlameTextBrowser` / `PyFlameTreeWidget`
        - **Fixed**
            - Setting `tooltip` to `None` did not remove the tooltip (the old text stayed and kept
              showing). It now removes it, like `PyFlameTable`. Creating a widget without a
              tooltip is unchanged.
    - `PyFlameImageGallery`
        - **Fixed**
            - `extensions` were case sensitive: `['.PNG']` matched no files. Extensions are now
              compared in lower case. The `extensions` property returns what was set, as before.
    - `PyFlameTokenMenu`
        - **Fixed**
            - `add_menu_options` emptied the dictionary the menu was created with, which is often the
              script's own dictionary, and gave an empty menu when called with that same dictionary.
              The script's dictionary is now left alone.
            - With no `token_dest` (the default `None`), picking a token from the menu raised an
              `AttributeError`. Picking a token with no destination now does nothing. Menus with a
              `PyFlameEntry` destination are unchanged.

- **Windows**
    - `PyFlameWindow`
        - **Fixed**
            - A `line_color` with an alpha value (`Color.BLUE_TRANS`, `Color.RED_TRANS`,
              `Color.YELLOW_TRANS`, `Color.GREEN_TRANS`, `Color.TEAL_TRANS`, `Color.UNDERLINE`)
              raised an error every time the window was drawn and could crash Flame. These colors
              now work in `PyFlameWindow` and every window built on it (`PyFlameMessageWindow`,
              `PyFlameOptionWindow`, `PyFlameInputDialog`, `PyFlamePasswordWindow`,
              `PyFlameProgressWindow`).
            - The `parent` type hint said any `QWidget` was accepted. It now says
              `PyFlameWindow | None`, which is what the window accepts.
            - The window could not be moved by clicking and dragging in the title area. It can now
              be dragged from the title the same as from any other empty part of the window. This
              also applies to every window built on `PyFlameWindow`.
            - Its docstring said the `grid_layout_*` properties can be set. Setting them after the window
              is created has no effect, as the grid is built once when the window is created. It now
              says so. Docstring only.
        - **New Argument**
            - `modal`
                - When set to `True`, the window blocks its parent window and stays above it until it
                  is closed. While it is open, Flame and every other open PyFlame window are blocked too. Only
                  takes effect when `parent` is given and showing when the window is created. Can't
                  be changed after the window is created.
                  (Default: `False`)
        - **New Behavior**
            - macOS: the window used to disappear whenever Flame was not the active application and
              come back when Flame was clicked on again. It now stays showing, on top of other
              applications. This also applies to every window built on `PyFlameWindow`. Nothing
              changes on Linux.
    - `PyFlameInputDialog`
        - **Fixed**
            - `line_color` was ignored and the line was always blue. The line now uses the given
              color.
            - Reading the `text` property raised an `AttributeError` if the window was closed without
              Ok or Cancel. It now returns `None`.
            - Errors for a wrong `parent` or `message_bar_text` named `PyFlameInputWindow`. They now
              name `PyFlameInputDialog`.
            - The window did not block its parent window, which could be clicked and brought in
              front of it. When a parent is given and showing, the window now blocks it and stays
              above it until closed. With no parent, or a hidden or closed parent, nothing changes.
    - `PyFlameMessageWindow`
        - **Fixed**
            - The window did not block its parent window, which could be clicked and brought in
              front of it. When a parent is given and showing, the window now blocks it and stays
              above it until closed. With no parent, or a hidden or closed parent, nothing changes.
    - `PyFlameOptionWindow`
        - **Fixed**
            - The window did not block its parent window, which could be clicked and brought in
              front of it. When a parent is given and showing, the window now blocks it and stays
              above it until closed. With no parent, or a hidden or closed parent, nothing changes.
    - `PyFlamePasswordWindow`
        - **Fixed**
            - The window did not block its parent window, which could be clicked and brought in
              front of it. When a parent is given and showing, the window now blocks it and stays
              above it until closed. With no parent, or a hidden or closed parent, nothing changes.
            - Any password was accepted when sudo had already been given the right password a short
              time before (sudo remembers it for a few minutes and then didn't read the typed one).
              The password is now always checked: the test runs `sudo -k -S`, which ignores the
              remembered password for that test only and doesn't clear it.
            - With `user_name_prompt=True`, Confirm (or Return) didn't close the window, so it could
              only be closed with Cancel, and Cancel after a Confirm still left the typed username and
              password in `username` and `password`. Confirm now closes the window with the username
              and password set. Cancel (or Escape) closes it and sets both to `None`. The password-only
              window is unchanged.
    - `PyFlameProgressWindow`
        - **Fixed**
            - The percentage in the progress text was one step behind: setting `current_task` showed
              the percentage of the previous task (the first task always showed `0.0%`). The text
              now shows the percentage of the task that was just set (`1 of 4` shows `25.0%`).
            - A `task_progress_message` that is not a string gave an error that showed the type of
              `parent` (`got NoneType`) instead of its own. It now shows the type of
              `task_progress_message`.

- **PyFlameFunctions**
    - `pyflame.print_list`
        - **Fixed**
            - `time` was ignored: messages in the Flame message area always showed for 3 seconds. They
              now show for `time` seconds. Without `time` (default `3`) nothing changes.
            - A `list_name` that is not a string raised a `NameError` instead of a `TypeError`. It now
              raises a `TypeError` that names `list_name`.
    - `pyflame.print_title` / `pyflame.create_media_panel_libraries`
        - **Fixed**
            - A wrong argument type (`text` not a string, `library_structure` not a dict) raised a
              `NameError` (`UnboundLocalError` for `create_media_panel_libraries`) instead of a
              `TypeError`. It now raises a `TypeError` that names the argument.
    - `pyflame.python_package_local_install`
        - **Fixed**
            - Its type errors now start with `pyflame.python_package_local_install`, like every other
              `pyflame` function (the `pyflame.` was missing).
    - `pyflame.verify_script_install`
        - **Fixed**
            - An `additional_files` that is not a list gave a garbled error
              (`verify_script_install.additional_files: Expected 'list' to be str, got str instead.`).
              It now says `pyflame.verify_script_install: Expected 'additional_files' to be list, got str instead.`
    - `pyflame.create_file_system_folder` / `pyflame.create_file_system_folders` /
      `pyflame.create_media_panel_folder` / `pyflame.create_media_panel_folders`
        - **Fixed**
            - The `create_file_system_folder` and `create_file_system_folders` docstring examples
              showed the top-level keys of `folder_structure` created as folders
              (`Shot001/Folder1/SubFolder1`). They are not: their contents are created inside the
              named folder (`Shot001/SubFolder1`). The examples of all four now say so, and
              `create_file_system_folder` says that with `skip_existing=True` only the first top-level
              key's contents are created. Docstring only: no code changed.
            - The docstring examples of `create_media_panel_folder` and `create_media_panel_folders`
              passed the workspace (`current_workspace`) as `dest`, which raises a `TypeError` (`dest`
              must be a Folder or Library). They now pass a library
              (`current_workspace.libraries[0]`). Docstring only: no code changed.
    - `pyflame.resolve_tokens`
        - **Fixed**
            - A batch group tag with no space after the colon (`ShotName:PYT_0010`) raised an
              `IndexError`. The tag value is now read with or without the space, and spaces around it
              are removed. `ShotName: PYT_0010` gives the same shot name as before. Also works with
              the `shot_name_tag` argument. An empty tag value (`ShotName:`) now falls back to the
              Render node shot name and then the batch group name. A tag value that itself holds
              a colon and a space (`ShotName: A: B`) now gives all of it (`A: B`), not just `A`.
            - A name with a backslash in it (project, user, clip, segment, tape, shot or batch group
              name) raised a `re.error` or was changed (`\n` became a line break). Names are now
              used exactly as they are. Names without a backslash give the same result as before.
            - Its docstring example called `pyflame.translate_path_tokens`, which doesn't exist. It
              now calls `pyflame.resolve_tokens`.
    - `pyflame.untar`
        - **Fixed**
            - Paths with spaces in them failed: the tar file path and destination path were split
              at the spaces. Paths are now passed to `tar` whole.
            - Without a sudo password the function didn't wait for `tar` to finish, so it could
              return `False` while the files were still being extracted, or `True` when `tar` failed
              but the destination folder already had files in it. It now waits for `tar` and
              returns `False` when `tar` fails. `tar`'s error output is printed on a failure.
            - With a sudo password, a failed `sudo` or `tar` (for example a wrong password) returned
              `True` when the destination folder already had files in it. It now returns `False`.
            - Its docstring said `sudo_password` is a `bool` and its example called `pyflame.unzip`.
              It now says `str | None` and the example calls `pyflame.untar`.
            - A `sudo_password` that is not a string or `None` gave an error that said
              `Expected 'None | sudo_password' to be str`. It now says
              `Expected 'sudo_password' to be str | None`.
    - `pyflame.shot_name_from_clip`
        - **Fixed**
            - A clip name made only of numbers (`0010`), or one that starts with a number followed by
              a separator (`0010_PYT`, `1_`), raised an `IndexError`. The parts of the name that are
              there are now used (`0010`, `0010_PYT`). Other clip names give the same shot name as
              before.
            - A clip tag with no space after the colon (`ShotName:PYT_0010`) raised an `IndexError`.
              It is now read, with spaces around the value removed (a value that itself holds a
              colon and a space is read as before). An empty value (`ShotName:`) gives an empty
              shot name. Tags with a space after the colon (`ShotName: PYT_0010`) are read exactly
              as before. Also works with the `shot_name_tag` argument.
            - With the `shot_name_tag` argument, the clip was tagged with the default `ShotName` tag
              name. It is now tagged with the given tag name.
            - When the shot name was worked out from the clip name, the clip was tagged with the
              shot name tag and all of its other tags were removed. Its other tags are now kept and
              the shot name tag is added to them.
    - `pyflame.shot_name_from_batch_group`
        - **Fixed**
            - A batch group tag with no space after the colon (`ShotName:PYT_0010`) raised an
              `IndexError`. It is now read, with spaces around the value removed (a value that
              itself holds a colon and a space is read as before). An empty value (`ShotName:`)
              gives an empty shot name. Tags with a space after the colon (`ShotName: PYT_0010`)
              are read exactly as before. Also works with the `shot_name_tag` argument.
            - With the `shot_name_tag` argument, the batch group was tagged with the default
              `ShotName` tag name. It is now tagged with the given tag name.
            - When the shot name was worked out from the batch group name, the batch group was
              tagged with the shot name tag and all of its other tags were removed. Its other tags
              are now kept and the shot name tag is added to them.
    - `pyflame.find_by_tag`
        - **Fixed**
            - With `sorted=True`, a `target_tag` written with no space after the colon
              (`ShotName:PYT_0010`) was used whole as the tag name, and a tag name also matched longer
              names (`ShotName` matched `ShotNameOld`). The tag name is now the part before the first
              colon and must match in full. Objects the binary search found before are still found
              the same way.
            - With `sorted=True`, an object that has the tag was not found when the searched objects
              were not sorted by tag, when some of them had no tag, or when another tag starting with
              the same name came first in an object's tags. When the binary search finds nothing, a
              linear search is now run as well. Objects the binary search finds are the same as before.
            - Its docstring said `pyobject` is a Library, Desktop or Folder, and its examples passed a
              Library. Flame can't search those directly (it raises a `TypeError`): `pyobject` must be a
              list of them, such as a Library's folders (`<PyLibraryObject>.folders`). The docstring,
              examples and type hint now say so. No code changed.
    - `pyflame.get_media_panel_shot_folder`
        - **Fixed**
            - A destination folder path with more than one folder (`Shot_Folder/Plates`) raised an
              `IndexError` when the destination folder had subfolders of its own. The destination
              folder is now returned.
            - A destination folder path with more than one folder raised an `AttributeError` when no
              shot folder was tagged with the shot name. It now returns `None`, as it already did for
              a single folder path. `pyflame.move_to_shot_folder` and `pyflame.copy_to_shot_folder`
              then print that the shot folder was not found, as they already did for a single folder
              path.
    - `pyflame.file_browser`
        - **Fixed**
            - `title=None` (the default) raised a `TypeError`. It now gives the title `Select File`
              when an `extension` is given and `Select Directory` when not, as an empty title already
              did. A given title is used as before.
    - `pyflame.convert_export_preset_name_to_path`
        - **Fixed**
            - `Project: Movie:` names gave a path with a space at the start of the file name
              (`movie_file/ Quicktime 4444.xml`). The space is gone.
            - A preset name that itself holds a colon and a space (`Shared: Movie: ProRes: HQ`) gave
              only the part before it (`ProRes.xml`). It now gives the whole name (`ProRes: HQ.xml`).
              Names in the documented forms without a colon in the preset name give the same path
              as before.
    - `pyflame.get_export_preset_names` / `pyflame.convert_export_preset_name_to_path`
        - **Fixed**
            - Project presets were looked for in `/opt/Autodesk/<project name>/export/presets/flame`,
              which is not where Flame keeps them, so `get_export_preset_names` never listed a
              Project preset and `convert_export_preset_name_to_path` gave a path to a file that
              didn't exist. The Project folders now come from Flame
              (`flame.PyExporter.get_presets_dir`). If Flame can't give them, the old path is used
              as before. Shared presets are unchanged.
    - `pyflame.create_temp_folder` / `pyflame.cleanup_temp_folder`
        - **Fixed**
            - A `folder_name` that led to the script's `lib`, `assets` or `config` folder (in any letter
              case, or through `..`) was accepted, and that folder was deleted. These now raise a
              `ValueError` before anything is created or deleted. Folders inside them (`assets/temp`)
              and every other name work as before.
            - A `folder_name` that led to the script folder itself or outside it (`''`, `'.'`, `'..'`,
              `'../x'`, an absolute path elsewhere, or a path through a symlink that points outside)
              deleted or emptied that folder. These now raise a `ValueError` and nothing is deleted or
              created. Folders inside the script folder (the default `temp`, `temp/sub`) work as
              before.

## v5.5.3 [10.16.26]

### Updates

- Changed license from GPL-3.0 to MIT. See LICENSE file for details.

## v5.5.2 [10.08.26]

### Updates

- Fixed "screenGeometry" error for Flame 2027.2

## v5.5.1 [08.11.26]

### Updates

- **Widgets**
    - `PyFlameMenu`
        - Updated stylesheet - menu bar now changes to grey when disabled.

- **PyFlameConfig**
    - Now neatly prints lists and dictionaries to the console.


## v5.5.0 [07.22.26]

### Updates

- **Widgets**
    - `PyFlameListWidget`
        - **Updated Stylesheet**
        - **New Argument**
            - `header`
                - Set the header text of the list widget. (Default: `None`)
            - `header_alignment`
                - Alignment of the header text. One of `Align.LEFT`, `Align.CENTER`, or `Align.RIGHT`.
                  (Default: `Align.CENTER`)

    -`PyFlameTreeWidget`
        - **Updated Stylesheet**
        - **New Argument**
            - `top_level_collapsible`
                - When set to `True`, top-level items can be collapsed and expanded, allowing them to
                  be used as collapsible category headers. Each top-level item with children is given an
                  animated disclosure triangle that points right when collapsed and rotates to point down
                  when expanded. Top-level headers keep a fixed darker-grey background; child rows under
                  them use alternating row colors. (Default: `False`)
            - `set_column_widths`
                - Dictionary mapping column names to their width in pixels. Only the columns included in
                  the dictionary are given a fixed width; any columns not included keep their default
                  resize-to-contents behavior. If `None`, no column widths are set.
                  (Default: `None`)
        - **New Property**
            - `set_column_widths`
                - Get or set the widths of individual columns using a dictionary that maps column names
                  to their width in pixels.
                  (Default: `None`)
        - **New Method Argument**
            - `add_item_with_columns()`
                - `parent`
                    - Item to add the new item under as a child. If `None`, the item is added as a
                      top-level item as before. Useful for grouping items under collapsible category
                      headers.
                      (Default: `None`)
        - **New Behavior**
            - Any item that has children now shows a disclosure arrow in the gutter. The arrow appears
              when a child is added and disappears once the item's last child is removed. The only
              exception is a top-level item in a non-collapsible tree (`top_level_collapsible` is
              `False`): those items stay expanded and cannot be collapsed, so they never show an arrow.

    -`PyFlameTextEdit`
        - **New Behavior**
            - Markdown text (`text_type` set to `TextType.MARKDOWN`) is now automatically styled as soon
              as it's set on the `text` property - no extra call required. Styling applied:
                - Headers (h1-h6) are colored gold. Header font sizes set by the Markdown rendering are
                  preserved.
                - `**bold**` spans are colored gold-tan. The bold weight is preserved.
                - `` `code` `` spans are colored with a dark background, outlined with a thin border
                  in the same color as the widget's regular text at 25% opacity, and kept in a
                  fixed-pitch (monospace) font.
                - Body text that falls under a header is indented. Headers themselves are never indented.
                - Text uses the Montserrat Light font at normal, non-condensed glyph widths (the condensed
                  stretch applied to the rest of the app's font is bypassed).

## v5.4.0 [06.03.26]

### Added

- **PyFlameOptionWindow**
    - New window class to display a message with up to four user-defined buttons along the bottom of the
      window. The window blocks until the user presses a button (or closes the window),
      then exposes the text of the pressed button.
    - Buttons are positional. Positions are defined using a dictionary keyed by an int from 1 to 4,
      where each value is a dictionary describing that button. Positions map directly to fixed columns
      along the bottom of the window, so omitting a position leaves an empty gap in that slot.

## v5.3.2 [05.25.26]

### Updates/Fixes

- **Widgets**
    -`PyFlameSlider`
        - **Fixed**
            - Numbers not being entered in calculator entry field when pressing number keys in linux.

## v5.3.1 [05.04.26]

### Updates/Fixes

- **Widgets**
    -`PyFlameTable`
        - load_csv()
            - Cells resize to fit content when data is added to the table.

- Misc type hinting and argument validation improvements.

## v5.3.0 [03.13.26]

- Lots of type hinting and argument validation improvements.

### Added

- **PyFlameImageWidget**
    - Image widget to display images.

- **PyFlameImageGallery**
    - Image gallery widget to display a gallery of images.

### Updates

- **Widgets**
    -`PyFlameTextEdit`
        - **New Method**
            - `set_focus()`
                - Sets focus of current window to PyFlameTextEdit
        - **New TextStyle**
            `READ_ONLY_SELECTABLE`
                - Text is not editable but is selectable and can be added to the clipboard (Copy/Paste).

    -`PyFlameMenu`
        - Menus with one or no menu items no longer show a dropdown menu. Text is only shown on menu button.

## v5.2.4 [02.28.26]

### Updates

- **Widgets**
    -`PyFlameWindow`
        - Added argument for window margins - defaults to 15.

## v5.2.3 [02.24.26]

### Updates/Fixes

- **Widgets**
    -`PyFlameSlider`
        - **Fixed**
            - Disaapearing calculator in linux.

### Added

- **PyFlame Library Stub File**
    - Stub file for better auto-completion in code editors.
      Be sure to rename this file as you would the pyflame_lib.py file.
      Example: <script_name>/lib/pyflame_lib_<script_name>.pyi
      Code editors should automatically import this file when the pyflame_lib.py file is imported.

## v5.2.2 [02.18.26]

- Fixed: Unable to find project errors in terminal when Flame starts up.

- **Widgets**
    - `PyFlameSlider`
        - **Calculator**
            - Pressing number keys now updates the value in the calculator entry field.
            - Pressing backspace key now deletes the last character in the calculator entry field.

- **PyFlameFunctions**
    - `pyflame.move_to_shot_folder`
        - Added `expand_dest_folder` argument to expand the destination folder after move is complete.
    - `pyflame.copy_to_shot_folder`
        - Added `expand_dest_folder` argument to expand the destination folder after copy is complete.

## v5.2.1 [01.08.26]

- Misc spelling/type-o fixes

## v5.2.0 [01.04.26]

### Updates/Fixes

- **Widgets**
    - `PyFlameLabel`
        - **Fixed**
            - `Enabled` argument wasn't working.
    - `PyFlameTabWidget`
        - **Fixed**
            - Widget wasn't properly spanning in gridlayout. This caused windows to not be sized properly.
            - Changed `enable` argument to `enabled` to be consistent with other widgets

- **Windows**
    - `PyFlameWindow`
        - **Fixed**
            - Window centering
        - **New Argument**
            - `message_bar`
                - Add message bar area to bottom of windows. Used to display short messages.
                  (Default: True)
        - **New Property**
            - `message_bar_text`
                - Use to set or get message bar text.

    - `PyFlameInputWindow`
        - **New Argument**
            -`message_bar`
                - Add message bar area to bottom of windows. Used to display short messages.
                  (Default: False)
        - **New Property**
            - `message_bar_text`
                - Use to set or get message bar text.

    - `PyFlameMessageWindow`
        - Added properties to docstring.
        - **New Argument**
            -`message_bar`
                - Add message bar area to bottom of windows. Used to display short messages.
                  (Default: False)
        - **New Property**
            - `message_bar_text`
                - Use to set or get message bar text.

    - `PyFlamePasswordWindow`
        - **New Argument**
            -`message_bar`
                - Add message bar area to bottom of windows. Used to display short messages.
                  (Default: False)
        - **New Property**
            - `message_bar_text`
                - Use to set or get message bar text.

    - `PyFlameProgressWindow`
        - Simplified arguments/properties.
        - **Fixed**
            - Added missing docstrings to properties.
        - **New Argument**
            -`message_bar`
                - Add message bar area to bottom of windows. Used to display short messages.
                  (Default: False)
        - **New Property**
            - `message_bar_text`
                - Use to set or get message bar text.
        - **New Methods**
            -`text_append`
                - Appends text to the currently displayed message
            -`pause`
                - Adds a delay in seconds to allow the UI time to refresh before moving on the the next operation.
            -`tasks_completed`
                - Sets completed state of progress window after tasks are done.
            -`enable_done_button`
                - Enabled the Done button.

## v5.1.1 [12.16.25]

### Updates/Fixes

- **Widgets**
    - `PyFlameProgressWindow`
        - **Misc Fixes**

## v5.1.0 [12.05.25]

### Added

- **PyFlameFunctions**
    - `pyflame.python_package_local_install`
        - New function to install python packages locally bundled with a script.

### Updates/Fixes

- **Widgets**
    - `PyFlameTreeWidget`
        - **New Methods**
            - `add_item_with_columns`
                - Add a new item to a tree with tree column entries.
            - `color_item`
                - Color item in tree.
            - `set_fixed_column_headers`
                - Set all tree column headers to a fixed length

## v5.0.0 [09.03.25]

**Major Rewrite of PyFlame Library**

This update will break most scripts using this library.

### New Features

- All widgets now have properties to simplify things and provide more consistency and commonality between all widgets.
  Previous widget arguments and methods may not longer work as expected.
  All new properties/methods are documented in the docstring of each widget.

### Added

- **Widgets**
    - `PyFlameProgressBarWidget` -
        - Progress bar widget to show progress of tasks

    - `PyFlameTextBrowser`
        - Text widget for displaying text with hyperlinks.
        - Has ability to display html, markdown, and plain text.

- **PyFlameFunctions**
    - `pyflame.get_media_panel_shot_folder`

    - `pyflame.move_to_shot_folder`

    - `pyflame.copy_to_shot_folder`

### Updates/Fixes

- **Widgets**
    - `PyFlamePushButton`
        - **New Methods**
            - `connect`
                - Connect a function to button press.
        - Argument changed: `button_checked` -> `checked`
        - instead of button.isChecked() to get checked state, use button.checked
        - instead of button.isEnabled() use button.enabled to get enabled state

    - `PyFlameTextEdit`
        - Added ability to display text as html, markdown, and plain text.

    - `PyFlameListWidget`
        - **New methods**
            - `replace_items` - Replaces all items in list with new list of items.

    - `PyFlameSlider`
        -Removed `use_float` argument. Whether the Slider is float or int is taken from min/max values.
        -Calculator window now closes when user clicks outside calculator window.

    - Renamed Widgets
        - `PyFlamePushButtonMenu` -> `PyFlameMenu`
        - `PyFlamePushButtonColorMenu` -> `PyFlameColorMenu`
        - `PyFlameTokenPushButton` -> `PyFlameTokenMenu`

- **Windows**
    - `PyFlameDialogWindow`
        - Class has been removed. Use `PyFlameWindow` instead.

    - `PyFlameWindow`
        - Now uses QDialog instead of QWidget.
        - **New Arguments**
            - `enter_pressed`
                -  Function to call when enter/return key is pressed on keyboard.
            - `escape_pressed`
                - Function to call when escape button is pressed on keyboard.

    - `PyFlameInputDialog`
        - **New Property**
            - `text`
                - Get or set input entry text.
        - **Returns**
            Ok - Input text string
            Cancel - None

### Misc

- Removed Support for PySide2.

- Removed: `max_width` and `max_height` arguments from all widgets.

- `PyFlameToolTip`
    - New class for adding tooltips to pyflame widgets. Not intended to be used directly.
    - Added delay and duration arguments. These can be used to set the delay and duration of the tooltip.

## v4.3.1 [04.16.25]

### Fixed

- **Widgets**
    - `PyFlameEntryBrowser` – Error when setting `connect=None`

## v4.3.0 [03.16.25]

### Added

- **Widgets**
    - `PyFlameTable`
        - A table widget that allows for displaying and interacting with tabular data such as CSV files.

    - `PyFlameTabWidget`
        - Creates a tab widget inside of a window that other widgets can be places inside of.

- **PyFlameFunctions**
  - `pyflame.print_title`
    - Prints title and version of script to terminal.

- **Windows**
    - `PyFlameInputDialog`
        - A simple dialog window that allows for input of a single line of text.

### Updates/Fixes

- **Widgets**
    - `PyFlameButton`
        - **New Arguments**
            - `max_height`
                - Set PyFlameButton to maximum height. Use if height is being set by layout. Overrides `height` if set to True.

    - `PyFlameEntry`
        - **New Methods**
            - `text_changed(connected_function: Callable)`:
                - Calls a function when the text in the entry field changes.

    - `PyFlameSlider`
        - Updated Calculator UI

    - `PyFlameTextEdit`
        - **New Arguments**
            - `text_type`
                - Set type of text being added using TextType enum. TextType.PLAIN, TextType.MARKDOWN, TextType.HTML.

    - `PyFlameColorPushButtonMenu`
        - **New Methods**
            - `get_color`
                - Return selected color name.
            - `get_color_value`
                - Return normalized RGB color value of selected color.
            - `set_color`
                - Set the color of the `PyFlameColorPushButtonMenu`.

        - `No Color` option added to default color menu. This either applies no color or clears the current color.

- **Windows**
    - `PyFlameWindow`/`PyFlameDialogWindow`
        - **New Methods**
            - `set_title_text`
                - Set the title of the window.

### Misc

- Added new file structure for libraries and assets.
    ```
    script_folder/
    ├── main_script.py
    ├── lib/
    │   └── pyflame_lib_<main_script_name>.py
    ├── assets/
    │   └── fonts/
    │       └── Montserrat-Regular.ttf
    │       └── Montserrat-Light.ttf
    ```

- To import the library in a script, use:
    `from lib.pyflame_lib_<main_script_name> import *`

## v4.2.0 [02.19.25]

### Added

- **Widgets**
    - `PyFlameEntryFileBrowser`
        - Replaces PyFlameLineEditFileBrowser which is now deprecated.

- **PyFlame Functions**
    - `pyflame.raise_type_error`
        - Raise a type error. Print error message with traceback to Flame message area and terminal.

    - `pyflame.raise_value_error`
        - Raise a value error. Print error message with traceback to Flame message area and terminal.

    - `create_temp_folder`
        - Create a temporary folder in the script folder.

    - `cleanup_temp_folder`
        - Clear the contents of the temporary folder.

### Updates/Fixes

- **Widgets**
    - `PyFlameEntry`
        - Improved tooltip functionality. Added arguments to set the tooltip delay and duration.
        - Added Alt+Click to show full entry text as tooltip. Also copies full entry text to clipboard.

    - PyFlameLabel
        - **New Style Option**
            - `Style.BACKGROUND_THIN`
                - Adds a darker background to the Label with a thinner font weight. Text is left aligned by default. Used for window titles.

    - `PyFlameListWidget`
        - **New Arguments**
            - `items`
                - A list of items to add to the list widget can now be provided on creation of the widget.

    - `PyFlamePushButton`
        - Improved tooltip functionality. Added arguments to set the tooltip delay and duration.

    - `PyFlameTextEdit`
        - **New Arguments**
            - `text_type`
                - Type of text being input. `TextType.PLAIN`, `TextType.MARKDOWN`, `TextType.HTML`

- **Windows**
    - `PyFlameWindow`/`PyFlameDialogWindow`
        - Fixed: Line colors not properly being applied to side of window.
        - **New Arguments**
            - `title_style`
                - Set style of title line in window. Use Style Enum to set style.
            - `parent`
                - Set parent of window.

### Deprecated

    - PyFlameLineEditFileBrowser
        - Use PyFlameFileBrowser instead.

    - LineColor Enum. All colors are now set using the Color Enum.

### Misc

- Updated font used for widgets. Montserrat Regular is now the default font for all QT widgets. The Discreet font is used
as a fallback if Montserrat is not found. Font location: `<SCRIPT_FOLDER>/assets/fonts`

- PyFlame Widget Argument Validation
    - Argument errors now print to Flame message area as well as terminal.

## v4.1.0 [01.15.25]

### Added

- **Widgets**
    - `PyFlameHorizontalLine`
        - A horizontal line widget.
    - `PyFlameVerticalLine`
        - A vertical line widget.

## v4.0.0 [01.05.25]

### Added

- **Widgets**
    - `PyFlameEntry`
        - Replaces `PyFlameLineEdit` which has been deprecated.
        - **New Arguments**
            - `align`
                - Align entry text to left, right, or center. Default is left.


- **PyFlameFunctions**
    - `create_media_panel_library`
        - Create a library with folders in the media panel based on the provided folder structure.

    - `create_media_panel_folder`
        - Create a single folder in the media panel based on the provided folder structure.

    - `create_media_panel_folders`
        - Create folders in the media panel from a list of folder names and a folder structure.

    - `create_file_system_folder`
        - Create a single folder in the file system based on the provided folder structure.

    - `create_file_system_folders`
        - Create folders from a list of folder names and a folder structure.

    - `print`
        - Print a message to the terminal and Flame message area. Replaces message_print function which has been deprecated.

    - `print_dict`
        - Cleanly print nested dictionaries with indentation to the terminal.

    - `print_json`
        - Cleanly print JSON data to terminal with proper indentation for easy readability.

    - `set_shot_tagging`
        - Tag Flame objects with shot name tag (ShotName: <shot_name>).

    - `verify_script_install`
        - Verify that script is installed in the correct location with any additional files that are required.

    - `find_by_tag`
        - Search through a Flame object's contained objects by tags.

    - `shot_name_from_clip`
        - Get shot name from clip.

    - `move_to_shot_folder`
        - Move a clip to a shot folder in the Media Panel.

    - `get_export_preset_names`
        - Get export preset names from Shared and Project paths. User paths are not checked.

    - `convert_export_preset_name_to_path`
        - Convert export preset name to path.

### Updates/Fixes

- **Widgets**
    - `PyFlameTextEdit`
        -`read-only` background color now matches read-only background color of PyFlameEntry for consistency.

    - `PyFlameTreeWidget`
        - **New Arguments**
            - `top_level_editable`
                - Allow editing of name of top level items in the tree. Default is False.
            - `tree_list`
                - List of items to populate the tree. Useful when dealing with batch group schematic reels shelf reels and desktop reels.
            - `tree_list_no_root`
                - List of items to populate the tree excluding the root item. Useful when dealing with batch group schematic reels shelf reels and desktop reels.
            - `update_callback`
                - Function to call when an item is edited, inserted, or deleted.

        - **New Attributes**
            - `selected_item`
                - Return the text of the currently selected item.
            - `item_path`
                - Return the recursive path of the currently selected item.
            - `item_paths`
                - Return the recursive paths of the currently selected items.
            - `all_item_paths`
                - Return the recursive paths of all items in the PyFlameTreeWidget.

    - `PyFlameGridLayout`
        - Added the ability to set the number of columns and rows in the grid to make it easier to place widgets especially where space is desired between widgets.
        By default the unit size of the grid is 150px wide and 28px high. The size of a normal button. The width and height of each grid unit along with the
        number of columns and rows can be adjusted using setGridSize method.
        - **New Arguments**
            - `columns`
                - Set number of columns in the grid. Default is 0.
            - `rows`
                - Set number of rows in the grid. Default is 0.
            - `column_width`
                - Set width of each column in the grid. Default is 150.
            - `row_height`
                - Set height of each row in the grid. Default is 28.
            - `adjust_column_widths`
                - Set width of specific columns in the grid. Default is {}.
            - `adjust_row_heights`
                - Set height of specific rows in the grid. Default is {}.

        - **New Methods**
            - `setGridSize`
                - Configure the grid layout dimensions and cell sizes. This method allows you to:
                - Set the number of columns and rows in the grid
                - Define the width of each column (in pixels)
                - Define the height of each row (in pixels)
                - Automatically adjust spacing between grid cells

        - **Arguments Removed**
            - `setMinimumColumnWidth`
                - No longer needed.
            - `setMinimumRowHeight`
                - No longer needed.


- **PyFlameFunctions**
    - `pyflame.copy_to_clipboard`
        - Type hinting made compatible with Flame 2024.

    - pyflame.generate_unique_node_names
        - Fixed: Would not properly generate a new name if the first character of the new name was a number.

    - pyflame.resolve_tokens
        - Batch groups are now checked for a ShotName tag(ShotName:<shot_name>). If found, it is used to resolve the shot name token.

- **Windows**

- `PyFlameWindow`/`PyFlameDialogWindow`
    - Simplified window creation by adding PyFlameGridLayout to the window by default with optional
        arguments to set the number of columns and rows along with column and row widths. This can
        be overridden by passing grid_layout=False.

    - **New Arguments**
        - `tab_width`
            - Set the width of tab name label
        - `tab_height`
            - Set the height of the tab name label
        - `grid_layout`
            - Set to True to use the default grid layout. Default is True.
        - `grid_layout_columns`
            - Set the number of columns in the grid layout. Default is 4.
        - `grid_layout_rows`
            - Set the number of rows in the grid layout. Default is 3.
        - `grid_layout_column_width`
            - Set the width of each column in the grid layout. Default is 150.
        - `grid_layout_row_height`
            - Set the height of each row in the grid layout. Default is 28.
        - `grid_layout_adjust_column_widths`
            - Set the width of specific columns in the grid layout. Default is {}.
        - `grid_layout_adjust_row_heights`
            - Set the height of specific rows in the grid layout. Default is {}.

- `PyFlameMessageWindow`
    - Updated message printing to terminal to be more clear.
    - Message text no longer uses html tags. Text is now printed as plain text.

- `PyFlameProgressWindow`
    - Updated message printing to terminal to be more clear.

### Deprecated

- **Widgets**
    - `PyFlameLineEdit`
        - Use PyFlameEntry instead.

    - `PyFlameLabel.Style.BACKGROUND`
        - Use PyFlameEntry with read_only=True instead.

- **PyFlameFunctions**
    - `pyflame.message_print`
        - Use pyflame.print instead.

    - `pyflame.resolve_path_tokens`
        - Use pyflame.resolve_tokens instead.

### Misc
    - `max_width` argument is now set to True by default for all widgets. width and height are now bypassed. This means the widgets will now expand to fill the available space. The size of the widgets is now determined by the layout(PyFlameGridLayout, PyFlameHBoxLayout, PyFlameVBoxLayout). To override this behavior, set max_width to False and set width and height arguments to set the size of the widget.

    - `max_height` argument is now set to True by default on the following widgets. The above behavior for `max_width` applies to max_height in these widgets:
        - PyFlameListWidget
        - PyFlameTreeWidget
        - PyFlameTextEdit

## v3.2.0 [09.09.24]

### Added

- **PyFlame Functions**
    - `pyflame.json_print`
        - Cleanly print JSON data to terminal with proper indentation for easy readability.

## v3.1.0 [09.01.24]

### Added

- **PyFlame Functions**
    - `pyflame.print_list`
        -  Print a list of items to the terminal and Flame message area.
    - `pyflame.print`
        - Print a message to the terminal and Flame message area.

### Updates/Fixes

- **Windows**
    - `PyFlameMessageWindow`
        - Added scrollbars to message window for long messages.

## v3.0.0 [08.16.24]

### Added

- **PyFlame Functions**
    - `pyflame.copy_to_clipboard`
        - Copy text to clipboard using QT.

### Updates/Fixes

- **Widgets**
    - `PyFlameTreeWidget`
        - Fixed font size issue in linux.
        - When sorting is enabled, sorting is done in ascending order of items in column 0.

- **Config**
    - `PyFlameConfig`
        - Config file is now saved as a JSON file. Values no longer need to be converted to strings before saving as before. Values are saved as their original data types.

- **Windows**
    - Message/Password/Progress Windows
        - Message text is now set to plain text format. HTML tags are no longer supported. Text appears as typed.
        - Added line wrap to message window text. Text will wrap to next line if it exceeds the window width.

    - `PyFlameProgressWindow`
        - Done button is now enabled once progress is complete. No need to manually set it to enabled.

### Misc
    - `_WindowResolution`
        - Utility class to determine the main window resolution based on the Qt version. Fixes conflicts with Shotgrid Toolkit and Flame 2025. Thanks to Ari Brown for this fix.

## v2.5.0 [06.22.24]

### Updates/Fixes

- **Widgets**
    - `PyFlameTreeWidget`
        - **New Attributes**
            - `tree_list`
                - Get a list of all item names in the tree. (Converted this to an attribute from a method)
            - `tree_dict`
                - Get a dictionary of all items in the tree.

### Misc

- Docstring improvements for richer IDE tooltips.

## v2.4.0 [06.12.24]

### Added

- **Pyflame Functions**
    - `pyflame.iterate_name`
        - Iterate through a list of names and return a unique name based on the list.

### Updates/Fixes

- **Widgets**
    - `PyFlameTreeWidget`
        - **New Methods**
            - `fill_tree`
                - Fill the tree widget with the provided dictionary.
            - `add_item`
                - Add a new item as a child of the currently selected item in the tree,
            - `delete_item`
                - Delete the selected item in the tree.
            - `sort_items`
                - Sort all items in the tree while maintaining the structure and keeping the tree expanded.
            - `tree_list`
                - Get a list of all item names in the tree.

## v2.3.0 [05.07.24]

### Added

- **Widgets**
    - `PyFlameButtonGroup`
        - Allows for grouping of PyFlameButtons, PyFlamePushButtons, PyFlamePushButtonMenus, and PyFlameColorPushButtonMenus.
          By default set_exclusive is set to True. This means only one button in the group can be selected at a time.

- **Pyflame Functions**
    - `pyflame.generate_unique_node_names`
        - Generate unique node names based on a list of existing node names.

## v2.2.0 [05.05.24]

### Misc

- Added constants for script name(SCRIPT_NAME), script path(SCRIPT_PATH). These are used as default values for script_name and script_path arguments in all classes and functions.
  Both constants are derived from the pyflame_lib file path and file name.
- Updated all classes and functions that have parameters for script_name and script_path.
  They now use SCRIPT_NAME constant for script name and SCRIPT_PATH constant for script path as default values if not passed as arguments.

## v2.1.16 [04.29.24]

### Updates/Fixes

- **Widgets**
    - `PyFlameDialogWindow`
        - Updated window layout to fix alignment issues with lines.

- **PyFlame Functions**
    - `pyflame.resolve_path_tokens`
        - Added BatchGroupName token. A PyBatch object must be passed as the flame_pyobject argument.

## v2.1.15 [04.23.24]

### Updates/Fixes

- **Widgets**
    - `PyFlameLineEdit`
        - **New Argument**
            - `tooltip`
                - Set tooltip text.

## v2.1.14 [04.16.24]

### Updates/Fixes

- **Config**
    - `PyFlameConfig`
        - **New Method**
            - `get_config_values`
                - Returns the values of a config file at the supplied path as a dictionary.

## v2.1.13 [04.01.24]

### Updates/Fixes

- **Config**
    - `PyFlameConfig`
        - Config file is saved if it doesn't exist when loading the default config values.

## v2.1.12 [03.08.24]

- **PyFlamePushButtonMenu** / **PyFlamePushButton** – new arg `enabled` (default True).

### Updates/Fixes

- **Widgets**
    - `PyFlamePushButtonMenu`
        - **New Argument**
            - `enabled`
                - Enable or disable button state. Default is True.

    - `PyFlamePushButton`
        - **New Argument**
            - `enabled`
                - Enable or disable button state. Default is True.

## v2.1.11 [03.03.24]

### Updates/Fixes

- **Widgets**
    - `PyFlameTokenPushButton`
        – Menu sizing fix to be consistent with other menus
    - `PyFlamePushButtonMenu`
        – Menu text is now left aligned.

## v2.1.10 [02.29.24]

### Added

- **Widgets**
    - `PyFlameColorPushButtonMenu`
        - Push Button Menu with color options. Returns selected color as a tuple of normalized RGB values.

- **Layout Classes**
    - `PyFlameGridLayout`
    - `PyFlameHBoxLayout`
    - `PyFlameVBoxLayout`

    These classes adjust values for margins, spacing, and minimum size for the layout using pyflame.gui_resize method
    so the layout looks consistent across different screen resolutions. Removes need to use pyflame.gui_resize inside
    of main script.

### Misc

- Improved argument validations for all widgets.
- Added arguments to turn off/on menu indicators for PyFlamePushButtonMenu and PyFlameColorPushButtonMenu. Default is off.

## v2.1.9 [02.17.24]

### Misc

- Tooltip text color set to white; tooltip border set to `1px solid black`.

## v2.1.8 [02.11.24]

### Misc
- UI/code improvements for Message/Progress/Password windows.

## v2.1.7 [02.09.24]

### Updates/Fixes

- **Pyflame Functions**
    - `get_flame_python_packages_path`
        – new arg to toggle terminal printing (default True).

- **Config**
    Fixed: Config values not printing in terminal when loading config file.

## v2.1.6 [01.31.24]

### Added

- **Widgets**
    - `PyFlameLineEditFileBrowser`
        - Line Edit widget that opens a flame file browser when clicked.

### Updates/Fixes

- **Widgets**
    - `PyFlameLineEdit`
        - **New Argument**
            - `read_only`
                - Makes the line edit read only and unselectable with dark background. Default is False.

    - `PyFlameSlider`
        - **New Argument**
            - `rate`
                - Controls the sensitivity of the slider. The value should be between 1 and 10. 1 is the most sensitive and 10 is the least sensitive. Default is 10.

        - **Fixed**
            - PySide6 errors/font in slider calculator.

## v2.1.5 [01.25.24]

### Updates/Fixes

- **Widgets**

- `PyFlameTokenPushButton`
    - **Argument Defaults**
        - `text='Add Token'`
        - `token_dict={}`
        - `token_dest=None`

    - **Added Argument Default Values**
        - `text='Add Token'`
        - `token_dict={}`
        - `token_dest=None`

    - **Methods**
        - `add_menu_options(new_options)`
            - Add new menu options to the existing token menu and clear old options.

## v2.1.4 [01.21.24]

### Misc

- Updated PySide.
- Improved UI scaling for different screen resolutions.
- Fixed issue with PyFlameConfig not properly returning boolean values.

## v2.1.3 [11.21.23]

### Updates/Fixes

- **Pyflame Functions**
    - `pyflame.get_export_preset_version()`
        - Checks default JPEG preset automatically.

## v2.1.2 [11.17.23]

### Updates/Fixes

- **Widgets**
    - `TokenPushButtonMenu`
        - Option to clear destination before insert.

## v2.1.1 [11.06.23]

### Added

- **Pyflame Functions**
    - `pyflame.get_export_preset_version()`
    - `pyflame.update_export_preset()`

## v2.1.0 [08.14.23]

### Misc

- Renamed all widgets from Flame* to PyFlame*.
- Improved widget docs; note that some widgets rely on others—keep them in this file.
