import os
from PIL import Image
from pathlib import Path
import random
import sys
import time
import argparse
import math
import subprocess as sp

os.system("")


class UserError(Exception):
    pass


HOME = Path.home()
SPRITE_FOLDER = os.path.join(HOME, ".config/sprites")


def twoPixel(top, bottom):
    if top[3] < 128 and bottom[3] < 128:
        return "\033[49m\033[39m "
    if top[3] < 128:
        return f"\033[49m\033[38;2;{bottom[0]};{bottom[1]};{bottom[2]}m▄"
    if bottom[3] < 128:
        return f"\033[49m\033[38;2;{top[0]};{top[1]};{top[2]}m▀"
    return f"\033[48;2;{top[0]};{top[1]};{top[2]}m\033[38;2;{bottom[0]};{bottom[1]};{bottom[2]}m▄"


def credit(name, width):
    txt = f"sprite by {name}"
    padding = 0
    if width > len(txt):
        padding = (width - len(txt)) // 2
    return (
        " " * width
        + "\n"
        + " " * padding
        + txt
        + " " * (width - padding - len(txt))
        + "\n"
    )


def load_image(path):
    basename = os.path.basename(path)
    name, ext = os.path.splitext(basename)
    author = None
    if " by " in name:
        parts = name.split(" by ")
        author = parts[-1]
    with Image.open(path) as im:
        if im.mode != "RGBA":
            raise UserError(f"{path} is not RGBA")
        res = im.copy()
    return res, author


def load_image2(path):
    with Image.open(path) as im:
        if im.mode != "RGBA":
            raise UserError(f"{path} is not RGBA")
        res = im.copy()
    return res


def search_image(width: None | int, height: None | int) -> tuple[Image.Image, str]:
    start = time.time()
    while True:
        path = os.path.join(SPRITE_FOLDER, random.choice(sprites))
        im = load_image2(path)
        if (
            (width is None or im.width <= width)
            and (height is None or math.ceil(im.height / 2) <= height)
        ) or time.time() - start > 0.1:
            return im, path


def get_image(
    path: None | int | str, width: None | int, height: None | int
) -> tuple[Image.Image, str]:
    if path is None:
        return search_image(width, height)

    if isinstance(path, int):
        if path <= 0 or path >= len(sprites):
            raise UserError("Invalid sprite index")
        path = os.path.join(SPRITE_FOLDER, sprites[path - 1])
        im = load_image2(path)
        return im, path

    return load_image2(path), path


def get_author(path: str) -> str:
    basename = os.path.basename(path)
    name, _ = os.path.splitext(basename)
    author = ""
    if " by " in name:
        parts = name.split(" by ")
        author = parts[-1]
    return author


def render_image(im: Image.Image, width: None | int, height: None | int):
    padding_w = 0
    crop_w = 0
    padding_h = 0
    crop_h = 0
    if width is not None:
        if width > im.width:
            padding_w = (width - im.width) // 2
        else:
            crop_w = (im.width - width) // 2
    else:
        width = im.width
    cheight = math.ceil(im.height / 2)
    if height is not None:
        if height > cheight:
            padding_h = (height - cheight) // 2
        else:
            crop_h = cheight - height

    res = ""

    res += (" " * width + "\n") * padding_h

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

    res += (" " * width + "\n") * padding_h

    return res


def image(
    path: None | int | str = None,
    width: None | int = None,
    height: None | int = None,
    show_author: bool = False,
    show_neofetch: bool = False,
):
    if show_author and height is not None:
        height -= 2

    im, path = get_image(path, width, height)

    author = get_author(path)

    image_txt = render_image(im, width, height)

    if show_author:
        if width is None:
            width = im.width
        image_txt += credit(author, width)

    if show_neofetch:
        combined = []
        neofetch_out = (
            # sp.run(["fastfetch", "-l", "none"], capture_output=True)
            sp.run(
                ["fastfetch", "-c", "neofetch", "-l", "none", "--pipe", "false"],
                capture_output=True,
            )
            # sp.run(["neofetch", "--off"], capture_output=True)
            .stdout.decode()
            .strip()
            .splitlines()
        )
        image_txt = image_txt.splitlines()

        if len(neofetch_out) > len(image_txt):
            image_txt_padding = (len(neofetch_out) - len(image_txt)) // 2
            neofetch_out_padding = 0
        else:
            neofetch_out_padding = (len(image_txt) - len(neofetch_out)) // 2 + 2
            image_txt_padding = 0

        for i in range(max(len(image_txt), len(neofetch_out))):
            if i >= image_txt_padding and i < len(image_txt) + image_txt_padding:
                combined.append("   " + image_txt[i - image_txt_padding])
            else:
                combined.append("   " + " " * len(image_txt[0]))

            if (
                i >= neofetch_out_padding
                and i < len(neofetch_out) + neofetch_out_padding
            ):
                combined[-1] += "   " + neofetch_out[i - neofetch_out_padding]

        image_txt = "\n".join(combined) + "\n"

    print(image_txt, end="")


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
    parser.add_argument(
        "--author",
        action="store_true",
        help="Display the author mentioned in the sprite filename behind de `by` keyword.",
    )

    parser.add_argument(
        "--neofetch",
        action="store_true",
        help="Display the neofetch output",
    )

    try:
        if not os.path.exists(SPRITE_FOLDER):
            raise UserError("`~/.config/sprites` do not exists")

        sprites = sorted(os.listdir(SPRITE_FOLDER))

        if len(sprites) == 0:
            raise UserError("No file in `~/.config/sprites`")

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
            image(sprite, args.width, args.height, args.author, args.neofetch)

    except UserError as e:
        print(f"Error: {e}")
