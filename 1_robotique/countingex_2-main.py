# Imports go at the top
from microbit import *
import music
import speech
import random


# Code in a 'while True:' loop repeats forever

"""
code demonstrateur avec 10 prgrammes
bouton a : incrémenter le programme
bouton b : executer
0
1
2
3
4
5
6
7
8
9

"""

p = 0 # programme
changed = False

while True:
    
    if button_b.was_pressed():
        p = p + 1
        display.show(p)
        changed = True
        if p == 10:
            p = 0
        
    if button_a.was_pressed():
        p = p - 1
        display.show(p)
        changed = True

    if changed:
        if p == 0:
                speech.say('zero')
        if p == 1:
                speech.say('one')
        if p == 2:
                speech.say('two')
        if p == 3:
                speech.say('three')
        if p == 4:
                speech.say('four')
        if p == 5:
                speech.say('five')
        if p == 6:
                speech.say('six')
        if p == 7:
                speech.say('seven')
        if p == 8:
                speech.say('eight')
        if p == 9:
                speech.say('nine')
        if p == -1:
                speech.say('minus one')
        if p == -2:
                speech.say('minus two')
        if p == -3:
                speech.say('minus three')
        if p == -4:
                speech.say('minus four')
        if p == -5:
                speech.say('minus five')
        if p == -6:
                speech.say('minus six')
        if p == -7:
                speech.say('minus seven')
        if p == -8:
                speech.say('minus eight')
        if p == -9:
                speech.say('minus nine')
        changed = False
    if button_a.is_pressed() and button_b.is_pressed():
        display.show(Image.HAPPY)
        if button_a.is_pressed() and button_b.is_pressed():
            music.play([''])
            