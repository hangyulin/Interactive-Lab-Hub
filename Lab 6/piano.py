# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import paho.mqtt.client as mqtt
import uuid

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
import pygame
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

music_script = deque([3,3,3,3,3,3,3,5,1,2,3,4,4,4,4,3,3,3,2,2,3,2,5,3,3,3,3,3,3,3,5,1,2,3,4,4,4,4,3,3,5,5,4,2,1])

# the # wildcard means we subscribe to all subtopics of IDD
topic = 'IDD/James'

#this is the callback that gets called once we connect to the broker. 
#we should add our subscribe functions here as well
def on_connect(client, userdata, flags, rc):
	print(f"connected with result code {rc}")
	client.subscribe(topic)
	# you can subsribe to as many topics as you'd like
	# client.subscribe('some/other/topic')

correct_keys = {'one':1, 'two':2, 'three':3, 'four':4, 'five':5}
# this is the callback that gets called each time a message is recived
def on_message(cleint, userdata, msg):
    instructions = msg.payload.decode('UTF-8')
    new_script = []
    for instruction in instructions:
        if instruction.isdigit():
            new_script.append(int(instruction))

    music_script.extend(new_script)
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

# this is blocking. to see other ways of dealing with the loop
#  https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#network-loop
client2.loop_forever()

# def play_key(key):
#     pygame.mixer.init()
#     if key == 1:
#         pygame.mixer.music.load("./sound/c.mp3")
#     elif key == 2:
#         pygame.mixer.music.load("./sound/d.mp3")
#     elif key == 3:
#         pygame.mixer.music.load("./sound/e.mp3")
#     elif key == 4:
#         pygame.mixer.music.load("./sound/f.mp3")
#     else:
#         pygame.mixer.music.load("./sound/g.mp3")
#     pygame.mixer.music.play()

# start with a blank screen
oled.fill(0)
# we just blanked the framebuffer. to push the framebuffer onto the display, we call show()
oled.show()
while True:
    if not music_script:
        next_text = 'DONE'
    else:
        next_text = 'Play ' + str(music_script[0])

    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.text((25, 5), next_text, font=font, fill="#0000FF")
    oled.image(image)
    # show all the changes we just made
    oled.show()
    if music_script and mpr121[music_script[0] + 5].value:
        client.publish("IDD/John", music_script[0])
        music_script.popleft()