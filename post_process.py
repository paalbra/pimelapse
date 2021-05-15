import argparse
import glob
import math
import pathlib
import re
import sys

from PIL import Image, ImageDraw, ImageFont, ImageStat


def brighten(pixel):
    return (math.log2(pixel+1)*32)-1


def get_average_brightness(image):
    image = image.copy().convert("L")
    return ImageStat.Stat(image).mean[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post process images")
    parser.add_argument("input", help="Glob patter to use for input images")
    parser.add_argument("--output", default="output", help="Output images direcory")
    args = parser.parse_args()

    output_dir_path = pathlib.Path(args.output)

    brightnesses = []

    for image_path in [pathlib.Path(path) for path in glob.glob(args.input)]:
        filename = image_path.name
        match = re.search(r"(?P<date>\d{8})_(?P<time>\d{6})\.(png|jpg)$", filename)
        if not match:
            raise ValueError(f"Filename has incorrect format: {filename}")

        date = re.sub(r"^(\d{4})(\d{2})(\d{2})$", r"\1-\2-\3", match.group("date"))
        time = re.sub(r"^(\d{2})(\d{2}).*$", r"\1:\2", match.group("time"))

        image = Image.open(image_path)
        overlay = Image.new(image.mode, image.size, (255,255, 255, 0))
        filestem = image_path.stem
        # extension = image_path.suffix
        extension = ".jpg"
        new_filename = f"{filestem}{extension}"
        new_image_path = output_dir_path.joinpath(new_filename)

        avg_brightness_pre = get_average_brightness(image)
        if avg_brightness_pre < 50:
            image = image.point(brighten)
        avg_brightness_post = get_average_brightness(image)
        brightnesses.insert(0, (avg_brightness_pre, avg_brightness_post))

        draw = ImageDraw.Draw(overlay)

        # Max and 50% brightness lines
        draw.line((0, image.size[1]-255, image.size[0], image.size[1]-255), fill=(0, 0, 0, 64))
        draw.line((0, image.size[1]-128, image.size[0], image.size[1]-128), fill=(0, 0, 0, 64))

        # Draw brightness graph
        for i in range(len(brightnesses)):
            width = 2
            if i*width >= overlay.size[0]:
                break
            brightness_pre, brightness_post = brightnesses[i]
            x = overlay.size[0]-width - i*width
            y1_pre = int(overlay.size[1]-1 - brightness_pre)
            y1_post = int(overlay.size[1]-1 - brightness_post)
            y2 = int(overlay.size[1]-2)
            draw.line((x, y1_post, x, y2), fill=(255, 255, 255, 192), width=width)
            if brightness_pre != brightness_post:
                draw.line((x, y1_pre, x, y2), fill=(128, 128, 128, 192), width=width)

        font_size = 32
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)

        # Brightness info as text
        x = image.size[0] - font_size*3
        y = image.size[1] - font_size
        draw.text((x, y), f"{avg_brightness_pre:.0f}", (128, 128, 128, 192), stroke_width=2, stroke_fill=(0, 0, 0, 128), font=font)
        draw.text((x, y-font_size), f"{avg_brightness_post:.0f}", (255, 255, 255, 192), stroke_width=2, stroke_fill=(0, 0, 0, 128), font=font)

        # Datetime as text
        draw.text((font_size, font_size), f"{date} {time}", (255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 128), font=font)

        image = Image.alpha_composite(image, overlay)
        image.convert("RGB").save(new_image_path)
        print(image_path, "=>", new_image_path)
