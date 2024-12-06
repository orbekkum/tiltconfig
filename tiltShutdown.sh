#!/bin/sh
set -e
cd /home/pi/OLED_Stats/
sudo -u pi python3 tiltShutdown.py
sudo shutdown -h now
