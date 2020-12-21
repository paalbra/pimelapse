import math
import sys

from PIL import Image, ImageDraw, ImageFont, ImageStat


def brighten(pixel):
    return (math.log2(pixel+1)*32)-1


def get_average_brightness(image):
    image = image.copy().convert("L")
    return ImageStat.Stat(image).mean[0]


image = Image.open(sys.argv[1])
filename = ".".join(sys.argv[1].split(".")[:-1])
# extension = sys.argv[1].split(".")[-1]
extension = "jpg"
new_filename = f"{filename}_2.{extension}"

avg_brightness = get_average_brightness(image)

if avg_brightness < 50:
    image = image.point(brighten)

avg_brightness_post = get_average_brightness(image)

font = ImageFont.truetype("DejaVuSans.ttf", 72)
draw = ImageDraw.Draw(image)
draw.text((72, 72), f"{avg_brightness:.2f}", (255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 128), font=font)
draw.text((72, 72*2), f"{avg_brightness_post:.2f}", (255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 128), font=font)

image.convert("RGB").save(new_filename)
print(new_filename)
