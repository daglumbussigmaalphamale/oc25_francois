from microbit import *
from machine import time_pulse_us
import KitronikMOVEMotor
import radio
import neopixel
import random

robot = KitronikMOVEMotor.MOVEMotor()
robot.move(0, 0)
robot.goToPosition(1, 90)

# le group doit correspondre au kit (1..15)
g = 1
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

trigger = pin13
echo = pin14

trigger.write_digital(0)
echo.read_digital()


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

def lights():
    for i in range(4):
        np[i] = random.choice(colors)
        np.show()

def blink(i, t0, t1, col, col2=black):
    t = running_time()
    if t % t0 < t1:
        np[i] = col
    else:
        np[i] = col2
    np.show()

def distance_cm():
    trigger.write_digital(1)
    trigger.write_digital(0)
    distance = time_pulse_us(echo,1)/2e6*340
    return round(distance)

while True:
    
    if button_a.was_pressed():
        robot.move(0, 0)
        prog = (prog + 1) % 10
        display.show(prog)
        

    if prog == 0:
        msg = radio.receive()
        if msg == 'u':
            left = pin1.read_analog()
            right = pin2.read_analog()
            d = (left - right)
            d = d // 10
            robot.move(10 - d, 10 + d)
        elif msg == 'd':
            robot.move(0,0)
        elif msg == '2':
            robot.goToPosition(1, 20)
        elif msg == '1':
            robot.goToPosition(1, 160)

    if prog==1:
        msg = radio.receive()
        left = pin1.read_analog()
        right = pin2.read_analog()
        d = (left - right)
        d = d // 10
        robot.move(10 - d, 10 + d)
        if distance_cm() <= 20:
            robot.move(0, 0)
        else:
            robot.move(10 - d, 10 + d)
        if msg=='d':
            robot.move(0, 0)
        if msg == '2':
            display.scroll(distance_cm(), 50)

    if prog==2:
        msg = radio.receive()
        if msg == 'u':
            robot.move(60,60)