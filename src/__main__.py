# -*- coding: utf-8 -*-

# Compatibility for both Python 2 and 3
# =======================================
from __future__ import absolute_import, print_function
__metaclass__ = type
try:
    input = raw_input
except NameError:
    pass
# =======================================

import ANSI
import copy
import displays
import glob
import os
import pickle
import subprocess
import sys
import time
import util
from PIL import Image

ARRANGEMENT = None
DIMENSIONS = None
PREFIX = 'TILE_'
IMAGES = []
COLS, ROWS = util.getTerminalSize()

def progressbar(left, index, total, right=None, skip=False, charset=3, mid_color=None):
    if right is None:
        right = '%s/%s ' % (index + 1, total) # Because index starts at 0 by default

    barload = COLS - len(right)
    if skip:
        div = int(total / barload)
        if div <= 0:
            div = 1

        if index > 1 and index % div != 0:
            return # Only print if progress bar advances

        left = '(Skipping) %s' % left

    # Progress section
    spaced = False # Put spaces in between progress bar characters
    advance = ['▮', '█', '▰', '⣿', '◼', '.', '⬜'][charset]
    remain = ['▯', '░', '▱', '⣀', '▭', ' ', '⣿'][charset]

    load = COLS - len(right) - len(left)
    mod = 1 if load % 2 == 0 else 0
    progress = int(index * barload / total) - len(left)
    if progress < 0:
        progress = 0

    # Left
    bar = ANSI.color(left, 'yellow')
    # Middle
    if mid_color is not None:
        bar += ANSI.color(mid_color)
    for i in range(load):
        if i == progress and mid_color is not None:
            bar += ANSI.color('reset')

        if spaced and i % 2 == mod:
            bar += ' '
        elif i < progress:
            bar += advance
        else:
            bar += remain
    # Right
    bar += ANSI.color(right, 'cyan')

    ANSI.move_column(1)
    print(bar, end='')
    sys.stdout.flush()

def progressclear():
    ANSI.clear(1)

def split():
    print('Splitting images...')
    start = time.time()
    converted = 0
    total = len(IMAGES)

    for index, image_file in enumerate(IMAGES):
        fname, ext = os.path.splitext(image_file)
        base = os.path.basename(fname)

        skip = False
        # Check if the glob gets expanded to existing files.
        # If it does, skip this image (already tiles for it)
        for some_file in glob.iglob('%s%s*' % (PREFIX, base)):
            skip = True
            break
        else: # Split the image
            try:
                image = Image.open(image_file)
            except IOError:
                progressclear()
                print(ANSI.color('Error: could not open "%s"' % image_file, 'red'))
                continue
            tiles = []

            imgw, imgh = image.size
            arrw, arrh = DIMENSIONS

            # Scale arrangement to best fit image
            # ===================================
            # Ratios
            imgr = imgw / imgh
            arrr = arrw / arrh

            scalew = False
            scaleh = False
            scale = 1
            xoffset = 0
            yoffset = 0
            new_arrw = 0
            new_arrh = 0

            # Image is smaller than arrangement
            if imgw < arrw and imgh < arrh:
                if imgr < arrr:
                    scaleh = True
                elif imgr > arrr:
                    scalew = True
            # Image is larger than arrangement
            elif imgw > arrw and imgh > arrh:
                if imgr < arrr:
                    scalew = True
                elif imgr > arrr:
                    scaleh = True
            # Image is wider than arrangement
            elif imgw > arrw:
                scaleh = True
            # Image is longer than arrangement
            elif imgh > arrh:
                scalew = True

            if scalew:
                scale = imgw * 1.0 / arrw
                new_arrh = int(arrh * scale)
                new_arrw = imgw
            elif scaleh:
                scale = imgh * 1.0 / arrh
                new_arrw = int(arrw * scale)
                new_arrh = imgh

            # Center arrangement if image is wider or longer
            if new_arrw < imgw:
                xoffset = int((imgw - new_arrw) / 2.0)
            if new_arrh < imgh:
                yoffset = int((imgh - new_arrh) / 2.0)

            new_arrangement = copy.deepcopy(ARRANGEMENT)

            for display in new_arrangement:
                display.w = int(display.w * scale)
                display.h = int(display.h * scale)
                display.x = int(display.x * scale) + xoffset
                display.y = int(display.y * scale) + yoffset

            for tile_index, display in enumerate(new_arrangement):
                area = (
                    display.x,              # Start x
                    display.y,              # Start y
                    display.x + display.w,  # End x
                    display.y + display.h   # End y
                )
                tile = image.crop(area)
                tile.save('%s%s_%d%s' % (PREFIX, base, tile_index, ext))

            converted += 1

        progressbar('"%s"' % image_file, index, total, skip=skip)

    end = time.time()
    progressclear()
    print(ANSI.color('Complete!', 'green'))

    duration = int(end - start)
    print(
        'Tiled %s files in %s seconds' % (
            ANSI.color(str(converted), 'cyan'),
            ANSI.color(str(duration), 'cyan')
        )
    )

def load_data():
    def load():
        try:
            with open(displays.DATA_FILE, 'rb') as file:
                global ARRANGEMENT
                ARRANGEMENT = pickle.load(file)
                return True
        except IOError:
            return False

    success = load()

    if success:
        print(ANSI.color('Successfully loaded!', 'green'))
    elif displays.find():
        success = load()

    return success

# Main
if __name__ == '__main__':
    args = sys.argv
    files = []

    prog = 'continuwall'
    usage = (
'''Welcome to image tile manager.
Split image(s) into tiles for each of your displays.

Usage: {0} <images>

Other commands:
    {0} clean                       remove tiles
    {0} clean <prefix>              remove tiles with specific prefix
    {0} config                      change your preferred arrangement
    {0} config <base64>             change your config using base64 (from share)
    {0} config <plist>              configure using this plist file
    {0} help                        display this help
    {0} prefix <prefix> <images>    specify a prefix for the tiles
    {0} share                       get your arrangement in base64 to easily share'''
    ).format(prog)

    num_args = len(args)
    if num_args == 1:
        print(usage)
        exit(0)

    command = args[1]
    if command == 'help':
        print(usage)
        exit(0)
    elif command == 'config':
        if num_args == 2:
            displays.find()
        elif num_args == 3:
            config = args[2]
            if os.path.isfile(config): # Specified plist file
                displays.find(config)
                exit(0)
            else: # Base64 shared arrangement
                import base64
                fname = displays.DATA_FILE

                decoded = ''
                try:
                    decoded = base64.b64decode(config)
                except Exception:
                    pass

                if decoded != '':
                    try:
                        with open(fname, 'wb') as file:
                            file.write(decoded)
                            print(ANSI.color('Successfully recorded!', 'green'))
                            exit(0)
                    except Exception:
                        pass

                print(ANSI.color('Error storing arrangement data in "%s"' % fname, 'red'))
        else:
            print(usage)
        exit(0)
    elif command == 'clean':
        if num_args == 2:
            pass
        elif num_args == 3:
            PREFIX = args[2]
        else:
            print(usage)
            exit(0)

        print('Removing all tiles with prefix "%s" ...' % PREFIX)
        removed = 0
        remove_files = glob.glob('%s*' % PREFIX)
        total = len(remove_files)
        for index, file in enumerate(remove_files):
            try:
                os.remove(file)
            except OSError:
                pass
            progressbar('"%s"' % file, index, total, mid_color='black')
            removed += 1

        progressclear()
        print(ANSI.color('Complete!', 'green'))
        print('Removed %s files' % ANSI.color(str(removed), 'cyan'))
        exit(0)
    elif command == 'prefix':
        if num_args < 4:
            print(usage)
            exit(0)

        PREFIX = args[2]
        files = args[3:]
    elif command == 'share':
        if not load_data():
            print('Could not determine display arrangement.')
            exit(0)

        try:
            with open(displays.DATA_FILE, 'rb') as file:
                import base64
                data = file.read()
                encoded = base64.b64encode(data)
                print('Here is your shareable arrangement data:')
                print(encoded)
        except IOError:
            print('Could not determine display arrangement.')
        exit(0)
    else:
        files = args[1:]

    if not load_data():
        print('Could not determine display arrangement.')
        exit(0)

    print('Using arrangement:')
    displays.print_arrangement(ARRANGEMENT)

    # Arrangement dimensions
    DIMENSIONS = displays.arrangement_size(ARRANGEMENT)

    IMAGES = [
        file for file in files
        if not file.startswith(PREFIX)
    ]

    try:
        split()
    except KeyboardInterrupt:
        progressclear()
        print(ANSI.color('Keyboard interrupt. Stopping...', 'red'))
