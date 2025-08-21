# Imports go at the top
from microbit import *
import music
import speech
import random


# Code in a 'while True:' loop repeats forever

x = 0
 
while True:
    if button_a.was_pressed():
        x = random.randint(1, 9)
        display.show(x)
    if button_b.was_pressed():
        a = x + 1
        display.show(a)
