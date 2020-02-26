# Project Name Source Code

The folders and files for this project are as follows:

**Original Code Modifications**
    Reuse dashboard.py. Want to add lives, downcount timer, 
        timer: should be set in the level json. then downtick until zero instead of uptick.
        Dashboard should be simple GUI, all manipulating functions should be in the controller.

    animation.py - Can be combined with sprite.py, sprites.py and spritesheet.py.
        separate the loadsprites function in sprites.py

    Abstract class for entity.py - want entity base to be implemented by subclasses of characters. Entity base will contain all the traits that were separated into (leftrightmovement, jump, bounce etc...)
        Checking a collision would be merged with the entity class as trait-like

    font should be a part of sprites (our opinion. shouldn't be separate). or part of GUI.

    Gaussian blur should be in maths or GUI since it only is a visual filter when game is paused.

    Controller - Interface for the functionality of the game.
        input.py
        Level.py (may be separate) could be placed in the controller.
        Camera.py functionality through controller.
        Entity - implement the movement trait.

    Maths.py - will turn into a helper class for physics based calculations (gravity).

    Menu.py might be placed and merged with dashboard, not too bad being left alone separate.

    Pause.py can be placed in Controller, or menu.

    Sound will remain separate.

    Tile.py - Make part of entity
        Can be entirely removed. does nothing
        it's just a data class, drawRect function does nothing. we can move this data elsewhere.

    The entities can be separate as they are.

    levels.json 

...
