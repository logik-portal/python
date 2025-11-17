"""
Script Name: Alternating Colours
Script Version: 1.0.0
Flame Version: 2025.1
Written by: Bryan Bayley
Creation Date: 08.14.24

Script Type: MediaPanel

Description:

    For any group of items selected in the Media Panel you can apply an alternating colour scheme (light/dark versions of the color you select).

    Only works when the items selected are the same type (Clip, Reel, Folder, etc.)

Menus:

    Right-click in Media Panel -> Alternating Colors

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.0.0 08.14.24
        - Initial release.
"""

# Colour pairs in a dictionary
COLOUR_SCHEMES = {
    "reds": [(96, 12, 12), (50, 0, 0)],
    "greens": [(29, 67, 45), (0, 50, 0)],
    "blues": [(48, 67, 102), (0, 0, 50)],
    "teals": [(0, 118, 118), (0, 50, 50)],
    "purples": [(99, 81, 138), (25, 0, 50)],
    "yellows": [(122, 122, 69), (50, 50, 0)],
    "oranges": [(150, 90, 40), (50, 25, 0)],
    "grays": [(90, 90, 90), (25, 25, 25)]
}

# Main function to apply alternating colours
def alternate_colours(selection, colour_scheme):
    import flame

    # Get the chosen colour pair from the dictionary
    colours = COLOUR_SCHEMES.get(colour_scheme.lower())

    if not colours:
        print(f"Colour scheme '{colour_scheme}' not found.")
        return

    for i, obj in enumerate(selection):
        obj.colour = colours[i % 2]  # Alternate colours based on index


# Specific functions for each colour scheme
def alternate_reds(selection):
    alternate_colours(selection, "reds")

def alternate_greens(selection):
    alternate_colours(selection, "greens")

def alternate_blues(selection):
    alternate_colours(selection, "blues")

def alternate_teals(selection):
    alternate_colours(selection, "teals")

def alternate_purples(selection):
    alternate_colours(selection, "purples")

def alternate_yellows(selection):
    alternate_colours(selection, "yellows")

def alternate_oranges(selection):
    alternate_colours(selection, "oranges")

def alternate_grays(selection):
    alternate_colours(selection, "grays")


### Scope of items that show the context menu entry ###

def scope_valid_objects(selection):
    import flame
    for item in selection:
        if isinstance(item, (flame.PyLibrary)):
            return True
        if isinstance(item, (flame.PyReelGroup)):
            return True
        if isinstance(item, (flame.PyReel)):
            return True
        if isinstance(item, (flame.PyFolder)):
            return True
        if isinstance (item, (flame.PyClip)):
            return True
    return False

### Context Menu ###

def get_media_panel_custom_ui_actions():

    return [
         {
            "name": "Alternating Colors",
            "actions": [
                {
                    "name": "Reds",
                    "isVisible": scope_valid_objects,
                    "execute": alternate_reds
                },
                {
                    "name": "Greens",
                    "isVisible": scope_valid_objects,
                    "execute": alternate_greens
                },
                {
                    "name": "Blues",
                    "isVisible": scope_valid_objects,
                    "execute": alternate_blues
                },
                {
                    "name": "Teals",
                    "isVisible": scope_valid_objects,
                    "execute": alternate_teals
                },
                {
                    "name": "Purples",
                    "isVisible": scope_valid_objects,
                    "execute": alternate_purples
                },
                {
                    "name": "Yellows",
                    "isVisible": scope_valid_objects,
                    "execute": alternate_yellows
                },
                {
                    "name": "Oranges",
                    "isVisible": scope_valid_objects,
                    "execute": alternate_oranges
                },
                {
                    "name": "Grays",
                    "isVisible": scope_valid_objects,
                    "execute": alternate_grays
                }

            ]
        }
    ]