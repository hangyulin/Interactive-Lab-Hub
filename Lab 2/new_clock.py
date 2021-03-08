import time
from datetime import datetime, timedelta
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789


# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

time_zone_version = 0

def get_image(version):
    if version == 0:
        image = Image.open("usa.png")
    elif version == 1:
        image = Image.open("uk.png")
    else:
        image = Image.open("china.png")
    
    # Scale the image to the smaller screen dimension
    image_ratio = image.width / image.height
    screen_ratio = width / height
    if screen_ratio < image_ratio:
        scaled_width = image.width * height // image.height
        scaled_height = height
    else:
        scaled_width = width
        scaled_height = image.height * width // image.width
    image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

    # Crop and center the image
    x = scaled_width // 2 - width // 2
    y = scaled_height // 2 - height // 2
    image = image.crop((x, y, x + width, y + height))

    return image


def display_time(version):
    the_time = datetime.now()
    if version == 1:
        the_time += timedelta(hours = 5)
    elif version == 2:
        the_time += timedelta(hours = 13)
    
    cur_time = the_time.strftime("%m/%d/%Y %H:%M:%S")

    y = top
    draw.text((x, y), cur_time, font=font, fill="#FFFFFF")

    hr = int(time.strftime('%H'))
    if hr > 19 or hr < 5:
        msg = 'Night time'
    else:
        msg = 'Day time'

    y = y + font.getsize(cur_time)[1]
    draw.text((x, y), msg, font=font, fill="#FF00FF")

    if version == 0:
        time_zone = 'EST'
    elif version == 1:
        time_zone = 'GMT'
    else:
        time_zone = 'CST'

    y = bottom - font.getsize(time_zone)[1] * 1.5
    draw.text((x, y), time_zone, font=font, fill="#0000FF")

    # Display image.
    disp.image(image)
    time.sleep(1)


while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    #TODO: fill in here. You should be able to look in cli_clock.py and stats.py
    display_time(time_zone_version)
    image = get_image(time_zone_version)
    if buttonB.value and not buttonA.value:
        time_zone_version = (time_zone_version + 1) % 3