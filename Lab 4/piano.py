# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

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

def play_key(key):
    pygame.mixer.init()
    if key == 1:
        pygame.mixer.music.load("./sound/c.mp3")
    elif key == 2:
        pygame.mixer.music.load("./sound/d.mp3")
    elif key == 3:
        pygame.mixer.music.load("./sound/e.mp3")
    elif key == 4:
        pygame.mixer.music.load("./sound/f.mp3")
    else:
        pygame.mixer.music.load("./sound/g.mp3")
    pygame.mixer.music.play()

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
    draw.text((25, 25), next_text, font=font, fill="#0000FF")
    oled.image(image)
    # show all the changes we just made
    oled.show()
    if music_script and mpr121[music_script[0] + 5].value:
        play_key(music_script[0])
        music_script.popleft()