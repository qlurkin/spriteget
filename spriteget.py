import os
from PIL import Image
from pathlib import Path
import random
import sys
import time
import argparse
import math

os.system("")

HOME = Path.home()
SPRITE_FOLDER = os.path.join(HOME, ".config/sprites")


class UserError(Exception):
    pass


def twoPixel(top, bottom):
    if top[3] < 128 and bottom[3] < 128:
        return "\033[49m\033[39m "
    if top[3] < 128:
        return f"\033[49m\033[38;2;{bottom[0]};{bottom[1]};{bottom[2]}m▄"
    if bottom[3] < 128:
        return f"\033[49m\033[38;2;{top[0]};{top[1]};{top[2]}m▀"
    return f"\033[48;2;{top[0]};{top[1]};{top[2]}m\033[38;2;{bottom[0]};{bottom[1]};{bottom[2]}m▄"


def load_image(path):
    with Image.open(path) as im:
        if im.mode != "RGBA":
            raise UserError(f"{path} is not RGBA")
        res = im.copy()
    return res


def image(path=None, width=None, height=None):
    if not os.path.exists(SPRITE_FOLDER):
        raise UserError("`~/.config/sprites` do not exists")

    sprites = sorted(os.listdir(SPRITE_FOLDER))

    if len(sprites) == 0:
        raise UserError("No file in `~/.config/sprites`")

    if path is None:
        start = time.time()
        while True:
            path = os.path.join(SPRITE_FOLDER, random.choice(sprites))
            im = load_image(path)
            if (width is None or im.width <= width) and (
                height is None or math.ceil(im.height / 2) <= height
            ):
                break
            if time.time() - start > 0.1:
                break

    else:
        if isinstance(path, int):
            if path <= 0 or path >= len(sprites):
                raise UserError("Invalid sprite index")
            path = os.path.join(SPRITE_FOLDER, sprites[path - 1])
        im = load_image(path)

    padding_w = 0
    crop_w = 0
    padding_h = 0
    crop_h = 0
    if width is not None:
        if width > im.width:
            padding_w = (width - im.width) // 2
        else:
            crop_w = (im.width - width) // 2
    cheight = math.ceil(im.height / 2)
    if height is not None:
        if height > cheight:
            padding_h = (height - cheight) // 2
        else:
            crop_h = cheight - height

    res = ""

    res += "\n" * padding_h

    for y in range(crop_h, ((im.height - crop_h) // 2) * 2, 2):
        res += " " * padding_w
        for x in range(crop_w, im.width - crop_w):
            res += twoPixel(im.getpixel((x, y)), im.getpixel((x, y + 1)))
        res += "\033[0m" + " " * padding_w
        res += "\n"

    if (im.height - crop_h) % 2 == 1:
        res += " " * padding_w
        for x in range(crop_w, im.width - crop_w):
            res += twoPixel(im.getpixel((x, (im.height - crop_h) - 1)), (0, 0, 0, 0))
        res += "\033[0m" + " " * padding_w
        res += "\n"

    res += "\n" * padding_h

    print(res, end="")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="spriteget",
        description="Display a random sprite from `~/.config/sprites` in Terminal",
    )

    parser.add_argument(
        "-s",
        "--sprite",
        help="path to the sprite file or integer. If it is an integer, it point to a file in `~/.config/sprites`",
    )
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        help="The number of characters that the sprite must take in width. If the sprite is smaller padding will be added and the sprite will be centered. If the sprite is larger it will be cropped. If the sprite is randomly selected, we will try to find one that is not larger.",
    )
    parser.add_argument(
        "--height",
        type=int,
        help="The number of characters that the sprite must take in height. If the sprite is smaller padding will be added and the sprite will be centered. If the sprite is larger it will be cropped. If the sprite is randomly selected, we will try to find one that is not larger.",
    )

    try:
        if len(sys.argv) < 2:
            image()
        else:
            args = parser.parse_args()
            sprite = args.sprite
            if sprite is not None:
                try:
                    sprite = int(sprite)
                except ValueError:
                    pass
            image(sprite, args.width, args.height)

    except UserError as e:
        print(f"Error: {e}")
