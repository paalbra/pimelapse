import datetime
import io
import time
from fractions import Fraction

import gpiozero
import picamera
from PIL import Image, ImageStat


def get_average_brightness(image):
    image = image.copy().convert("L")
    return ImageStat.Stat(image).mean[0]


def capture(shutter_speed, iso=800, exposure_mode="off"):
    stream = io.BytesIO()
    camera = picamera.PiCamera(resolution=(1024, 768), framerate=Fraction(1, 6), sensor_mode=3)
    camera.shutter_speed = shutter_speed
    camera.iso = iso
    camera.exposure_mode = exposure_mode

    camera.start_preview()
    time.sleep(1)
    camera.capture(stream, format="png")
    stream.seek(0)
    camera.close()

    return stream


filename = datetime.datetime.now().strftime(r"still_%Y%m%d_%H%M%S.png")

shutter_speed = 500_000
max_shutter_speed = 6_000_000
min_shutter_speed = 1_000

wanted_brightness = 128

led17 = gpiozero.LED(17)
led17.on()
time.sleep(1)

best_image = None
best_brightness = None
best_brightness_delta = 256

print(datetime.datetime.now().isoformat(timespec="seconds"), "START")

for x in range(5):
    stream = capture(shutter_speed)
    image = Image.open(stream)
    brightness = get_average_brightness(image)
    brightness_delta = abs(wanted_brightness-brightness)
    factor = wanted_brightness/brightness
    new_shutter_speed = int(shutter_speed*factor)

    print(
        datetime.datetime.now().isoformat(timespec="seconds"),
        f"seq={x}",
        f"ss=[{shutter_speed:,} => {new_shutter_speed:,}]",
        f"brightness=[{brightness:,.2f}*{factor:,.2f} ~= {wanted_brightness}]"
    )

    if brightness_delta < best_brightness_delta:
        best_image = image
        best_brightness = brightness
        best_brightness_delta = brightness_delta

    if shutter_speed == max_shutter_speed:
        print(datetime.datetime.now().isoformat(timespec="seconds"), "BREAK max shutter speed")
        break
    elif shutter_speed == min_shutter_speed:
        print(datetime.datetime.now().isoformat(timespec="seconds"), "BREAK min shutter speed")
        break
    else:
        shutter_speed = max(min(new_shutter_speed, max_shutter_speed), min_shutter_speed)

print(datetime.datetime.now().isoformat(timespec="seconds"), f"Best brightness: {best_brightness:,.2f}", f"Saving {filename}")
best_image.save(filename)

led17.off()

print(datetime.datetime.now().isoformat(timespec="seconds"), "STOP")
