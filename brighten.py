import math
import sys

from PIL import Image, ImageDraw, ImageFont, ImageStat


def brighten(pixel):
    return (math.log2(pixel+1)*32)-1


def get_average_brightness(image):
    image = image.copy().convert("L")
    return ImageStat.Stat(image).mean[0]

brightnesses = []

for image_path in sys.argv[1:]:
    image = Image.open(image_path)
    overlay = Image.new(image.mode, image.size, (255,255, 255, 0))
    filename = ".".join(image_path.split(".")[:-1])
    # extension = image_path.split(".")[-1]
    extension = "jpg"
    new_filename = f"{filename}_2.{extension}"

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

    # Brightness info as text
    font_size = 32
    font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    x = image.size[0] - font_size*3
    y = image.size[1] - font_size
    draw.text((x, y), f"{avg_brightness_pre:.0f}", (128, 128, 128, 192), stroke_width=2, stroke_fill=(0, 0, 0, 128), font=font)
    draw.text((x, y-font_size), f"{avg_brightness_post:.0f}", (255, 255, 255, 192), stroke_width=2, stroke_fill=(0, 0, 0, 128), font=font)

    image = Image.alpha_composite(image, overlay)
    image.convert("RGB").save(new_filename)
    print(new_filename)
