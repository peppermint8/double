# Doubleback 2
My first mostly complete python game.  Based on the game "Doubleback" for the TRS-80 color computer.  The original ran in 4kb of memory.

I wrote this using the pygame library as a learning experience. 

This is a Youtube video of the original: https://www.youtube.com/watch?v=3QLHdEeAAiI

## Installation
The game runs in python 3 and uses python libraries for pygame and yaml which do not come with the vanilla python 3 installation.

I used mamba (conda) to install the libs.


## Playing
Run the game by running `./doubleback.py` 
 - ENTER to select a menu option
 - use the mouse to move player 1 around
 - player 2 uses the keyboard (arrow keys or keypad) to move
 - P or ESC to pause, ESC again will exit the current game


The idea of the game is to encircle items in your tail to get points.  Some items don't move, some move randomly, some move towards you.  Encircling multiple items gives bonuses (2x, 3x or 4x the points value of the items)  Some items (skulls) don't disappear when you circle them.

## Config
The config file for the game is "config.yaml" which has lots of configuration options.  I kept with some themes from the old TRS-80 Color Computer for colors.  Its easy to modify your own game, just get some icons or images and edit the config to include them.  You can do different themed levels as well.  

You can include other configs and play them game by adding them to the command line:
`./doubleback.py d2.yaml` 
 - where d2.yaml is an alternate config

I got most of the icons from:
 - https://icons8.com/icon/set/logos/fluency
 - https://www.pngegg.com/

I got most of the sounds from:
 - https://mixkit.co/free-sound-effects/


## Known Problems
I'm not happy with how the controls for player 2 work with the keyboard.  I wish it was smoother like the mouse.  Currently set to a style like the old Tron light cycles game.

The level text can overwrite when the score increase passes more than one level. 

Also, sometimes the bounding box made by enclosing an item doesn't include the item IN the enclosure.  Blame Chat-GPT for that one.  (I suppose I could google a better answer also)

I tried to include code to prevent items from appearing too close to the player but its not perfect.

