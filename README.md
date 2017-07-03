## About
`ContinuWall` is an image tile manager written in Python. It's primarily serves to split a wallpaper into separate images for each of your displays.

## Features
- Split countless images: `continuwall wallpaper_dir/*`
- Configure to your exact display setup: `continuwall config`
    - (will do this automatically the first time)

## Install
> First you will need to install [Pillow](https://pypi.python.org/pypi/Pillow/2.2.1#installation)
Then simply run `sudo ./setup install`

## Why?
Because at work I was given a triple monitor setup, but the displays were not the same size. When I tried to split a wallpaper into even thirds, it didn't look right.  
Maybe cropping a single wallpaper would be easy, but if you're like me, you want a program like this so you can try hundreds ^^;

## Platforms
Currently `ContinuWall` only supports Mac. Future support for other OS's is unlikely, but feel free to contribute and make a pull request.
