# Imports go at the top
from microbit import *
import neopixel


# Code in a 'while True:' loop repeats forever
np = neopixel.NeoPixel(pin8, 60)
while True:
    if button_b.was_pressed():
        np[0] = (63, 63, 0)
        np.show()

