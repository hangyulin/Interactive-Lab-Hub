# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import paho.mqtt.client as mqtt
from PIL import Image, ImageDraw, ImageFont
import uuid
import time
import board
import digitalio
import adafruit_rgb_display.st7789 as st7789
import busio
import adafruit_ssd1306

from board import SCL, SDA
from adafruit_apds9960.apds9960 import APDS9960

start = time.time()

# Setup SPI bus using hardware SPI:

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

spi = board.SPI()

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
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)

# Every client needs a random ID
client = mqtt.Client(str(uuid.uuid1()))
# configure network encryption etc
client.tls_set()
# this is the username and pw we have setup for the class
client.username_pw_set('idd', 'device@theFarm')

#connect to the broker
client.connect(
    'farlab.infosci.cornell.edu',
    port=8883)

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)
apds = APDS9960(i2c)
apds.enable_proximity = True
apds.enable_gesture = True

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
image_oled = Image.new("1", (oled.width, oled.height))
draw_oled = ImageDraw.Draw(image_oled)

# the # wildcard means we subscribe to all subtopics of IDD
topic = 'IDD/James'

#this is the callback that gets called once we connect to the broker. 
#we should add our subscribe functions here as well
def on_connect(client, userdata, flags, rc):
	print(f"connected with result code {rc}")
	client.subscribe(topic)
	# you can subsribe to as many topics as you'd like
	# client.subscribe('some/other/topic')


# Every client needs a random ID
client2 = mqtt.Client(str(uuid.uuid1()))
# configure network encryption etc
client2.tls_set()
# this is the username and pw we have setup for the class
client2.username_pw_set('idd', 'device@theFarm')

# attach out callbacks to the client
client2.on_connect = on_connect


#connect to the broker
client2.connect(
    'farlab.infosci.cornell.edu',
    port=8883)

oled.fill(0)
# we just blanked the framebuffer. to push the framebuffer onto the display, we call show()
oled.show()

w = 15
h = 15
x1 = 50
y1 = 50
x2 = 200
y2 = 100
w2 = 25
h2 = 25
time_counter = 0.0
cur_direction = 1
speed = 8

all_direction = {0:(0, -1), 1:(0, 1), 2:(-1, 0), 3:(1, 0)}

def calculate_next_coor(x1, y1, direction, speed):
    new_x1 = x1 + all_direction[direction][0] * speed
    new_y1 = y1 + all_direction[direction][1] * speed

    if 0 <= new_x1 <= width - w and 0 <= new_y1 <= height - h:
        return new_x1, new_y1
    
    return x1, y1

# this is the callback that gets called each time a message is recived
def on_message(cleint, userdata, msg):
    global x2, y2, w2, h2
    coor = msg.payload.decode('UTF-8')
    new_coor = [int(t) for t in coor.split(',')]
    x2 = new_coor[0]
    y2 = new_coor[1]
    w2 = new_coor[2]
    h2 = new_coor[3]
    

client2.on_message = on_message

def isRectangleOverlap(self, R1, R2):
    if (R1[0]>=R2[2]) or (R1[2]<=R2[0]) or (R1[3]<=R2[1]) or (R1[1]>=R2[3]):
        return False
    else:
        return True

while True:
    gesture = apds.gesture()
    if gesture != 0:
        cur_direction = gesture - 1
        print(cur_direction)

    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    # old_x1, old_y1 = x1, y1
    x1, y1 = calculate_next_coor(x1, y1, cur_direction, speed)
    # if (x1, y1) == (old_x1, old_y1):
    #     cur_direction = (cur_direction + 1) % 4

    draw.rectangle((x1, y1, x1 + w, y1 + h), outline=0, fill=(0, 100, 0))
    
    draw.rectangle((x2, y2, x2 + w2, y2 + h2), outline=0, fill=(100, 0, 0))

    disp.image(image, rotation)

    client2.loop()

    draw_oled.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw_oled.text((45, 8), str(time_counter), font=font, fill="#0000FF")
    oled.image(image_oled)
    # show all the changes we just made
    oled.show()

    client.publish("IDD/John", ','.join([str(x1), str(y1), str(w), str(h)]))

    time_counter = int(divmod(time.time() - start, 3600)[1] % 60)

    if isRectangleOverlap([x1, y1, x1 + w, y1 + h], [x2, y2, x2 + w, y2 + h]):
        draw.text((30, 30), 'LOSE', font=font2, fill="#0000FF")
        disp.image(image, rotation)
        break

    elif time_counter >= 50:
        draw.text((30, 30), 'WIN', font=font2, fill="#0000FF")
        disp.image(image, rotation)
        break
