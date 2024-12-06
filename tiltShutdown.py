import time
import board
import busio
import digitalio

from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

import subprocess
import requests
from datetime import datetime

# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)

# Display Parameters
WIDTH = 128
HEIGHT = 64
BORDER = 5

#Control brewing
MINTEMP = 18.0
OG = 1.062

# Use for I2C.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

# Clear display.
oled.fill(0)
oled.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = oled.width
height = oled.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# Icons website: https://icons8.com/line-awesome
font = ImageFont.truetype('PixelOperator.ttf', 16)

data = '{"on": false}'
headers = {"Content-Type": "application/json"}

r = requests.put("http://10.0.0.1/api/<id>/lights/4/state", data=data, headers=headers)
print(r.status_code)
print(r.json())

# Text memory usage
draw.text((x, top+5), "Shutting down!",  font=font, fill=255)
oled.image(image)
oled.show()
