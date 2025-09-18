"""
TP robot 2

Nom: Hanyang
Classe: 3M5
Date: ...
No du robot: 2

Dans ce TP vous allez explorer comment
- prog 0 : télécommander le robot et la pince
- prog 1 : télécommander et changer la vitesse
- prog 2 : faire clignoter les 4 LED de façon aléatoire
- prog 4 : faire clignoter les 4 LED de façon régulier
- prog 5 : 4 dessins de noel et une musique
- prog 6 : visuliser un capteur de lumière avec 25 LED
- prog 7 : visuliser deux capteurs de lumière avec 2 barres à 5 LED
- prog 8 : suivre une ligne
"""

from microbit import *
from machine import time_pulse_us
import KitronikMOVEMotor
import music
import radio
import neopixel
import random

robot = KitronikMOVEMotor.MOVEMotor()
robot.move(0, 0)
robot.goToPosition(1, 90)

trigger = pin13
echo = pin14

trigger.write_digital(0)
echo.read_digital()

def distance_cm():
    trigger.write_digital(1)
    trigger.write_digital(0)
    distance = time_pulse_us(echo, 1)/2e6*340*100
    return round(distance)
    
# le group doit correspondre au kit (1..15)
g = 2
display.scroll(g)
radio.on()
radio.config(group=g)

prog = 0 # programme actuel (0..9)
display.show(prog)

red = (100, 0, 0)
green = (0, 100, 0)
blue = (0, 0, 100)

yellow = (100, 100, 0)
cyan = (0, 100, 100)
magenta = (100, 0, 100)
orange = (100, 50, 0)

black = (0, 0, 0)
white = (100, 100, 100)

colors = (black, red, orange, yellow, green, cyan, blue, magenta, white)

np = neopixel.NeoPixel(pin8, 4)
sleep(1000)
for i in range(4):
    np[i] = black
np.show()

hexa = '0123456789ABCDEF'
v = 4 # vitesse actuelle


def avancer(d):
    # avancer ou reculer de d centimètres
    d0 = 10.3 # distance de calibration
    if d>0:
        robot.move(120, 120, 20)
        robot.move(60, 60, d/d0*1000)
    else:
        robot.move(-120, -120, 20)
        robot.move(-60, -60, -d/d0*1000)

def tourner(a):
    # pivoter un angle a degrés
    d = a / 140 * 1000
    if a>0:
        robot.move(120, -120, 10)
        robot.move(60, -60, d)
    else:
        robot.move(-120, 120, 10)
        robot.move(-60, 60, -d)

while True:

    
    # le bouton A incrémente les programmes (0..9)
    if button_a.was_pressed():
        robot.move(0, 0)
        prog = (prog + 1) % 10
        display.show(prog)
        music.pitch(440, 20)

    # faire bouger le robot avec les 4 touches de direction
    # L/R pour pivoter, U/D pour avancer et reculer
    # F1: ouvrir la pince, F2: fermer la pince
    if prog == 0:
        msg = radio.receive()
        if msg:
            display.show(msg)
            if msg == '0':
                robot.move(0, 0)
            elif msg == 'u':
                robot.move(-150, -150)
            elif msg == 'r':
                robot.move(150, -150)
            elif msg == 'l':
                robot.move(-150, 150)
            elif msg == 'd':
                robot.move(150, 150)
            elif msg == '2':
                robot.goToPosition(1, 20)
            elif msg == '1':
                robot.goToPosition(1, 160)
                
    # suivre une ligne
    if prog == 1:
        msg = radio.receive()
        if msg=='u':
            left = pin1.read_analog()
            right = pin2.read_analog()
            d = (left - right)
            d = d // 10
            #if distance_cm() <= 10:
                #robot.move(0, 0)
            #else:
               # robot.move(10 - d, 10 + d)
                
        #if msg=='d':
           # robot.move(0, 0)

        #if msg == '2':
           # display.scroll(distance_cm(), 50)
        #if msg == '1':
        
    
