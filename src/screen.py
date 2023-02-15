#!/usr/bin/python3
# -*- coding:utf-8 -*-
import logging
import random

from pathlib import Path
import epaper
from PIL import Image, ImageDraw, ImageFont

WIDTH = 800
HEIGHT = 480


def show_image(black_image, red_image, clear=False):
    try:
        logging.info("Updating screen")

        epd = epaper.epaper("epd7in5b_V2").EPD()
        epd.init()
        if clear:
            epd.Clear()
        epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
        logging.info("Goto Sleep...")
        epd.sleep()

    except IOError as e:
        logging.info(e)


def show_random_image():
    mydir = Path("pictures")
    pictures = list(mydir.glob("*"))
    im = Image.open(pictures[random.randint(0, len(pictures) - 1)])
    resized = im.resize((WIDTH, HEIGHT))
    imnew = resized.convert("1")
    empty_image = Image.new("1", (WIDTH, HEIGHT), 255)
    show_image(imnew, empty_image, clear=True)


def show_plugs(plugs):
    list_plugs = list(plugs)

    bw_image = Image.new("1", (WIDTH, HEIGHT), 255)
    red_image = Image.new("1", (WIDTH, HEIGHT), 255)
    draw_bw_image = ImageDraw.Draw(bw_image)
    draw_red_image = ImageDraw.Draw(red_image)

    dim_y = int(HEIGHT / max(len(list_plugs), 4))
    font = ImageFont.truetype("Font.ttc", int(dim_y * 0.8))
    onoff_dim = font.getbbox("OFF1")
    onoff_x_pos = WIDTH - onoff_dim[2]
    for i, plug in enumerate(list_plugs):
        draw_bw_image.text((50, (i + 0.1) * dim_y), plug[0], font=font, fill=0)
        if plug[1]:
            on_dim = font.getsize("ON")
            draw_red_image.rounded_rectangle(
                [
                    onoff_x_pos - int(0.1 * on_dim[0]),
                    (i + 0.95) * dim_y - on_dim[1],
                    onoff_x_pos + on_dim[0] * 1.1,
                    (i + 0.95) * dim_y,
                ],
                radius=25,
                fill=0,
            )
            draw_red_image.text(
                (onoff_x_pos, (i + 0.1) * dim_y), "ON", font=font, fill=255
            )
        else:
            draw_bw_image.text(
                (onoff_x_pos, (i + 0.1) * dim_y), "OFF", font=font, fill=0
            )

    show_image(bw_image, red_image)
