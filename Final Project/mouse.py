# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import paho.mqtt.client as mqtt
import uuid
import time

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

import board
import busio
import adafruit_ssd1306
# import pygame
import adafruit_mpr121
from collections import deque
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

mpr121 = adafruit_mpr121.MPR121(i2c)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

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

time_counter = 0.0
while True:
    client2.loop()

    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.text((25, 5), str(time_counter), font=font, fill="#0000FF")
    oled.image(image)
    # show all the changes we just made
    oled.show()

    client.publish("IDD/John", str(time_counter))
    time.sleep(0.5)
    