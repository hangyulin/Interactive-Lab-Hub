# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import paho.mqtt.client as mqtt
from PIL import Image, ImageDraw, ImageFont
import uuid
import time
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
import busio
import adafruit_ssd1306

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

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

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

# this is the callback that gets called each time a message is recived
def on_message(cleint, userdata, msg):
    instructions = msg.payload.decode('UTF-8')
    print(instructions)
    
	# you can filter by topics
	# if msg.topic == 'IDD/some/other/topic': do thing


# Every client needs a random ID
client2 = mqtt.Client(str(uuid.uuid1()))
# configure network encryption etc
client2.tls_set()
# this is the username and pw we have setup for the class
client2.username_pw_set('idd', 'device@theFarm')

# attach out callbacks to the client
client2.on_connect = on_connect
client2.on_message = on_message

#connect to the broker
client2.connect(
    'farlab.infosci.cornell.edu',
    port=8883)

oled.fill(0)
# we just blanked the framebuffer. to push the framebuffer onto the display, we call show()
oled.show()

w = 10
h = 10
x1 = 50
y1 = 50
time_counter = 0.0
while True:
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    draw.rectangle((x1, y1, x1 + w, y1 + h), outline=0, fill=(5, 100, 0))
    disp.image(image, rotation)

    client2.loop()

    draw_oled.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw_oled.text((25, 5), str(time_counter), font=font, fill="#0000FF")
    oled.image(image_oled)
    # show all the changes we just made
    oled.show()

    client.publish("IDD/John", str(x1) + ',' + str(y1))
    time.sleep(0.5)
    time_counter += 0.5
    x1 += 5
    y1 += 5
