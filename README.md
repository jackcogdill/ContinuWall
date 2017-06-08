## What?
`Tile.sh` splits images into tiles by given dimensions.

![](http://i.imgur.com/oGNlLsX.png)

## Why?
Having been given a triple monitor setup, I wanted to use those widescreen wallpapers that stretch across all the displays. However, on Mac you need three separate images in order to do that. ImageMagick can easily do that for one image, but of course I wanted to test out hundreds of wallpapers ^^;  
Thus I wrote this script.

## Examples

`./Tile.sh 3 1 monkeyflower.jpg` turns this:

![](http://i.imgur.com/9Hwm2i1.jpg)
into this:

Tile 1                                 |  Tile 2                               |  Tile 3
:-------------------------------------:|:-------------------------------------:|:-------------------------------------:
![](http://i.imgur.com/bN0EcDA.jpg)    |  ![](http://i.imgur.com/PgtoBDi.jpg)  |  ![](http://i.imgur.com/bNtA4MF.jpg)

`./Tile.sh 3 2 257828.jpg` turns this:

![](http://i.imgur.com/mCGRuRr.jpg)
into this:

Tile 1                                 |  Tile 2                               |  Tile 3
:-------------------------------------:|:-------------------------------------:|:-------------------------------------:
![](http://i.imgur.com/kuLR0Pm.jpg)    |  ![](http://i.imgur.com/5N4Z0LV.jpg)  |  ![](http://i.imgur.com/pCWAnsP.jpg)
![](http://i.imgur.com/Hs3PnHc.jpg)    |  ![](http://i.imgur.com/Dj32kg8.jpg)  |  ![](http://i.imgur.com/C5RogXZ.jpg)
**Tile 4**                             |  **Tile 5**                           |  **Tile 6**
