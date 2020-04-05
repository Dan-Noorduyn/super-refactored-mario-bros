## Super Refactored Mario Bros.

Welcome Mario fans!

Our group has worked diligently to provide to you an authentic Super Mario Bros. experience. This version is open-source and will always be open for additions. We hope this recreation of the original game will be accessible to newer audiences as much as the old, without the hassle of emulating the original game.

With that being said; here are some things to keep in mind.

### Installation Guide

The game requires that the user have a working version of Python 3 that is compatible with your Operating System. This can be found at the link [here](https://www.python.org/)



To install the game, users are asked to download the project files from [here](https://gitlab.cas.mcmaster.ca/jandricd/super-refactored-mario-bros). 

Alternatively, you can clone the project repository from your preferred terminal:

```bash
$ git clone https://gitlab.cas.mcmaster.ca/jandricd/super-refactored-mario-bros.git
```



With the project files downloaded, there are a few more things to download so that the game can run, these are;

- pygame
- scipy

First, ensure that you have an appropriate version of pip for python. If you do not, it can be installed with the following command from your terminal.

*Note: pip should already be installed if you installed a version of Python3 greater or equal to 3.4*

##### For Windows

```bash
C: curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
C: python3 get-pip.py
```

##### For Ubuntu/Debian Systems

```bash
$ sudo apt install python3-pip
```

##### For MacOS Systems

```

```

Now that Python and Pip are installed, it's time to install pygame and scipy, the following command can be run from any terminal of your preference.

```
pip3 install scipy pygame
```

Now you're ready to roll!

### Starting the game

to get the game started, you will need to change directory from your preferred terminal until you are in the same directory as the game file.

from the home directory of the game, perform these commands:

```Bash
./super-refactored-mario$ cd src/mariopy/
```

You should now be in the mariopy directory and be able to execute the main.py file.

Type the command:

```
$ python3 main.py
```

If the game is successfully running, your terminal should display:

```
pygame 1.9.6
Hello from the pygame community. https://www.pygame.org/contribute.html
```

And the game window should also pop up on your screen.

Enjoy!

### Uninstalling the game

To uninstall the game, simply delete the files from its location in your Operating System's file explorer. The game does not create any artifacts on your computer.

### Controls

| Action      | Keyboard Key       |
| ----------- | ------------------ |
| Up          | Up-arrow, Spacebar |
| Left        | Left-arrow         |
| Right       | Right-arrow        |
| Boost       | Shift key (hold)   |
| Pause, Exit | Esc key            |

