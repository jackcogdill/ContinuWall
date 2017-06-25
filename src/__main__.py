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
PREFIX = 'TILE_'
IMAGES = []
COLS, ROWS = util.getTerminalSize()

def progressbar(left, index, total, right=None, skip=False, charset=3, mid_color=None):
    if right is None:
        right = '%s/%s ' % (index, total)

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
            image = Image.open(image_file)

            # image.save('%s%s%s' % (PREFIX, base, ext))

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

    prog = args[0]
    usage = (
'''Welcome to image tile manager.
Split image(s) into tiles for each of your displays.

Usage: {0} <images>

Other commands:
    {0} clean                       remove tiles
    {0} clean <prefix>              remove tiles with specific prefix
    {0} config                      change your preferred arrangement
    {0} help                        display this help
    {0} prefix <prefix> <images>    specify a prefix for the tiles'''
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
        displays.find()
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
        remove_files = glob.glob('%s*' % PREFIX)
        total = len(remove_files)
        for index, file in enumerate(remove_files):
            try:
                os.remove(file)
            except OSError:
                pass
            progressbar('"%s"' % file, index, total, mid_color='black')

        progressclear()
        print(ANSI.color('Complete!', 'green'))
        exit(0)
    elif command == 'prefix':
        if num_args < 4:
            print(usage)
            exit(0)

        PREFIX = args[2]
        files = args[3:]
    else:
        files = args[1:]

    if not load_data():
        print('Could not determine display arrangement.')
        exit(0)

    print('Using arrangement:')
    displays.print_arrangement(ARRANGEMENT)

    IMAGES = [
        file for file in files
        if not file.startswith(PREFIX)
    ]

    split()
