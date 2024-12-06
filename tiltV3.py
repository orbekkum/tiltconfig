import time
import board
import busio
import digitalio

from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

import subprocess
import requests
from datetime import datetime

from gpiozero import MotionSensor

pir = MotionSensor(17)

# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)

# Display Parameters
WIDTH = 128
HEIGHT = 64
BLACK = 0
WHITE = 255

# Display Refresh
LOOPTIME = 2.0

#Control brewing
MINTEMP = 22.5
MAXTIME = 1000
#OG = 1.062

# Use for I2C.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

# Clear display.
oled.fill(BLACK)
oled.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = oled.width
height = oled.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
draw.rectangle((0,0,width,height), outline=0, fill=0)

# First define some constants to allow easy resizing of shapes.
padding = -5
top = padding
#bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 1

# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# Icons website: https://icons8.com/line-awesome
font = ImageFont.truetype('PixelOperator.ttf', 18)
icon_font= ImageFont.truetype('lineawesome-webfont.ttf', 18)

draw.text((x, top+5),  "Starting up",  font=font, fill=WHITE)
draw.text((x, top+25),  "Temp: {}".format(MINTEMP),  font=font, fill=WHITE)
oled.image(image)
oled.show()
time.sleep(10)

while True:

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=BLACK, fill=BLACK)
    #clear()

    f = open("/home/pi/log.csv","r")
    for line in f:
        pass
    lastLine=line.split(",")
    f.close()

    fh=float(lastLine[2])
    Temperature=(fh-32)*5/9

    data = '{"on": false}'
    heaticon = 61956
    headers = {"Content-Type": "application/json"}

    timestamp = lastLine[0]
    in_time = datetime.strptime(timestamp, "%m/%d/%Y %I:%M:%S %p")
    now = datetime.now()
    diff = now - in_time
    minutes = divmod(diff.total_seconds(),60)
    Clock = datetime.strftime(in_time, "%H:%M")
    if diff.total_seconds() > MAXTIME:
       Clock = "OLD"
#       oled.invert(True)

    if diff.total_seconds() < MAXTIME and Temperature < MINTEMP:
        data = '{"on": true}'
        heaticon = 61957

    try:
        r = requests.put("http://10.0.0.2/api/<id>/lights/4/state", data=data, headers=headers)
    except Exception as e:
        draw.text((x, top+5),  "ERROR",  font=font, fill=WHITE)
        draw.text((x, top+25),  "Connecting to HUE",  font=font, fill=WHITE)
        draw.text((x, top+45),  "{}".format(e),  font=font, fill=WHITE)
        oled.image(image)
        oled.show()

    SG = lastLine[3]
    #Alcohol = (OG - float(SG)) * 131.25

    # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d\' \' -f1 | head --bytes -1"
    IP = subprocess.check_output(cmd, shell = True )

    # Icons
    # Icon temperature
    draw.text((x, top+5),    chr(62153),  font=icon_font, fill=WHITE)
    # Icon fire
    draw.text((x+65, top+5), chr(62570),  font=icon_font, fill=WHITE)
    # Icon flask
    draw.text((x, top+25), chr(61635),  font=icon_font, fill=WHITE)
    # Icon lightbulb
    draw.text((x+65, top+25), chr(61675), font=icon_font, fill=WHITE)
    # Icon wifi
    #draw.text((x, top+45), chr(61931),  font=icon_font, fill=WHITE)
    # Icon clock
    draw.text((x+65, top+45), chr(61463),  font=icon_font, fill=WHITE)

    # Text
    draw.text((x+19, top+5),  "{:.1f}".format(Temperature),  font=font, fill=WHITE)
    draw.text((x+87, top+5), chr(heaticon),  font=icon_font, fill=WHITE)
    draw.text((x+19, top+25), SG,  font=font, fill=WHITE)
    #draw.text((x+87, top+25), "{:.1f}".format(Alcohol), font=font, fill=WHITE)
    draw.text((x+87, top+25), "{}".format(r.status_code), font=font, fill=WHITE)
    #draw.text((x+19, top+45), "{}".format(r.status_code),  font=font, fill=WHITE)
    draw.text((x, top+45), str(IP,'utf-8'),  font=font, fill=WHITE)
    draw.text((x+87, top+45), "{}".format(Clock),  font=font, fill=WHITE)

    if pir.motion_detected:
        oled.image(image)
        oled.show()
    else:
        oled.fill(0)
        oled.show()
    time.sleep(LOOPTIME)
