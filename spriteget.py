import os
from PIL import Image
from pathlib import Path
import random

os.system("")

HOME = Path.home()
SPRITE_FOLDER = os.path.join(HOME, ".config/sprites")

if not os.path.exists(SPRITE_FOLDER):
    raise Exception("`~/.config/sprites` do not exists")

sprites = os.listdir(SPRITE_FOLDER)

if len(sprites) == 0:
    raise Exception("No file in `~/.config/sprites`")


def twoPixel(top, bottom):
    if top[3] < 128 and bottom[3] < 128:
        return "\033[49m\033[39m "
    if top[3] < 128:
        return f"\033[49m\033[38;2;{bottom[0]};{bottom[1]};{bottom[2]}m▄"
    if bottom[3] < 128:
        return f"\033[49m\033[38;2;{top[0]};{top[1]};{top[2]}m▀"
    return f"\033[48;2;{top[0]};{top[1]};{top[2]}m\033[38;2;{bottom[0]};{bottom[1]};{bottom[2]}m▄"


def image(path):
    with Image.open(path) as im:
        if im.mode != "RGBA":
            raise Exception("Use RGBA image")

        res = ""

        for y in range(0, (im.height // 2) * 2, 2):
            for x in range(im.width):
                res += twoPixel(im.getpixel((x, y)), im.getpixel((x, y + 1)))
            res += "\033[0m\n"

        if im.height % 2 == 1:
            for x in range(im.width):
                res += twoPixel(im.getpixel((x, im.height - 1)), (0, 0, 0, 0))
            res += "\033[0m\n"

    print(res, end="")


image(os.path.join(SPRITE_FOLDER, random.choice(sprites)))
