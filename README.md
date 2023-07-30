# Tilemap Editor for 2D Games

This is a tilemap editor written in Pygame. The program provides a graphical interface for building
tile-based environments for 2D applications. It processes the data and exports it as a .csv file. Right
now this only works with a spritesheet/textures atlas, but soon there will be additional compatibility.

There is an optional config to produce a "data mapper" for your .csv. This will export a .JSON file which
contains useful data for each item. As of writing this, it exports a key value pair, the key being the tile name,
the value being a dictionary container the ID and position of the tile on the spritesheet.

There is a decent amount of customization in this project. You can change:

- Background
- Tilemap Background? (optional)
- Tilemap grid colors? (optional)
- Tilemap canvas size (Mandatory)

All configurations are made in the "config.json" file. I find this to be more intuitive than having to click through
a ton of menus on startup.