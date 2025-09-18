# Imports go at the top
from microbit import *


# Code in a 'while True:' loop repeats forever
from machine import time_pulse_us

trigger = pin13
echo = pin14

trigger.write_digital(0)
echo.read_digital()

while True:
    trigger.write_digital(1)
    trigger.write_digital(0)
    distance = time_pulse_us(echo, 1)/2e6*340
    display.scroll(str(round(distance)))