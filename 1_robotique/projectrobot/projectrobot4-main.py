# Imports go at the top
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
g = 2
display.scroll(g)
radio.on()
radio.config(group=g)

prog = 0 # programme actuel (0..9)
display.show(prog)

# === Couleurs ===
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
v = 4 # vitesse actuelle (non utilisé directement ci-dessous, tu peux t’en servir)

# === Calibrations à ajuster pour TON robot ===
# --- Nouveau: paramètres pour la manoeuvre avant la prise ---
BACK_OFF_CM = 8                 # recul avant de tourner (à ajuster)
FORWARD_SEARCH_TIMEOUT_MS = 6000 # combien de temps on avance pour retrouver l'objet après le 180
# Distance/temps pour avancer (cm -> ms)
D_CAL_CM_PER_SLOW = 10.3  # utilisé par ta fonction avancer()
# Conversion angle -> ms pour pivoter
TURN_CAL_1000MS_PER_140DEG = 1000  # déjà dans ta tourner(a)
# Suivi de ligne
LINE_SPEED = 20          # vitesse de base en suivi
LINE_K = 0.08            # gain correcteur (plus grand = plus réactif)
# Ultrason
DIST_THRESH_PICK = 12    # seuil (cm) pour considérer l'objet atteint
DIST_APPROACH_MAX = 40   # distance (cm) max à laquelle on commence l'approche lente
# Pince (servo ch. 1) – ajuste selon ta mécanique
GRIP_OPEN = 160
GRIP_CLOSED = 20
# Sécurités/délais
APPROACH_SPEED = 18
RETURN_BONUS_MS = 400    # marge au retour vs durée aller (ms)
RELEASE_BACK_MS = 600    # petit recul après dépose (ms)

# === Fonctions de base existantes (légers ajustements) ===
def avancer(d):
    # avancer ou reculer de d centimètres
    d0 = 10.3 # distance de calibration (cm pour 1000ms à ~60)
    if d > 0:
        robot.move(120, 120, 20)
        robot.move(60, 60, d/d0*1000)
    else:
        robot.move(-120, -120, 20)
        robot.move(-60, -60, -d/d0*1000)

def tourner(a):
    # pivoter un angle a degrés (a>0 = droite, a<0 = gauche)
    d = a / 140 * 1000
    if a > 0:
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
    return max(0, min(400, round(distance*100)))  # en cm borné [0..400]

# === Fonctions ajoutées pour la mission A→B, prise, 180°, retour A ===
def set_all(color):
    for i in range(4):
        np[i] = color
    np.show()

def grip_open():
    robot.goToPosition(1, GRIP_OPEN)

def grip_close():
    robot.goToPosition(1, GRIP_CLOSED)

def follow_line_step(base=LINE_SPEED, k=LINE_K):
    """
    Une itération de suivi de ligne avec 2 LDR (pin1=left, pin2=right).
    Hypothèse: sol clair, ligne sombre -> valeur plus faible sur capteur au-dessus de la ligne.
    """
    left = pin1.read_analog()
    right = pin2.read_analog()
    # erreur: positif si la ligne est plus à droite (right < left)
    error = (left - right)
    correction = int(k * error)
    # limite les vitesses
    l = max(-100, min(100, base - correction))
    r = max(-100, min(100, base + correction))
    robot.move(l, r)

def follow_line_until_object(dist_thresh=DIST_THRESH_PICK, max_ms=30000):
    """
    Suit la ligne jusqu’à détecter un objet à 'dist_thresh' cm.
    Retourne la durée (ms) réellement parcourue et un booléen 'trouvé'.
    """
    set_all(blue)  # suivi A→B
    t0 = running_time()
    while running_time() - t0 < max_ms:
        d = distance_cm()
        # Approche lente si on s'approche d'un obstacle
        if d <= DIST_APPROACH_MAX:
            # ralentir progressivement
            base = max(12, int(LINE_SPEED * 0.6))
        else:
            base = LINE_SPEED
        follow_line_step(base=base)
        if d <= dist_thresh and d > 0:
            robot.move(0, 0)
            return running_time() - t0, True
        sleep(5)
    robot.move(0, 0)
    return running_time() - t0, False

def approach_until(dist_thresh=DIST_THRESH_PICK):
    """
    Avance tout droit doucement jusqu’à 'dist_thresh' cm de l'objet
    (utile si on n’était pas exactement dessus à la fin du suivi).
    """
    set_all(cyan)
    while True:
        d = distance_cm()
        if 0 < d <= dist_thresh:
            robot.move(0, 0)
            return True
        robot.move(APPROACH_SPEED, APPROACH_SPEED)
        sleep(10)

def turn_180():
    set_all(magenta)
    tourner(180)
    robot.move(0, 0)

def follow_line_for_ms(duration_ms):
    """
    Suit la ligne pendant 'duration_ms' millisecondes (utilisé pour le retour).
    """
    set_all(yellow)  # retour B→A
    t0 = running_time()
    while running_time() - t0 < duration_ms:
        follow_line_step(base=LINE_SPEED)
        sleep(5)
    robot.move(0, 0)

def mission_A_to_B_pick_and_return():
    """
    Pipeline demandé:
      - suivre la ligne A→B
      - détecter et s'approcher de l'objet (ultrason)
      - fermer la pince
      - 180°
      - revenir en suivant la ligne jusqu'à A (même durée que l'aller + petite marge)
      - poser l'objet et reculer
    """
    display.show('A')
    grip_open()
    set_all(blue)

    # 1) A -> B en suivant la ligne jusqu'à l'objet
    t_out, found = follow_line_until_object()
    if not found:
        set_all(red)
        display.scroll("OBJ?", 60)
        return  # échec: pas d'objet détecté

    # 2) Approche fine si besoin
    approach_until(DIST_THRESH_PICK)
    
    #reculer avant de chopper l'objet
    set_all(orange)
    avancer(-BACK_OFF_CM)
    sleep(150)
    
    # 4) 180°
    turn_180()
    sleep(200)

    #reculer avant de chopper l'objet
    set_all(orange)
    avancer(-BACK_OFF_CM)
    sleep(150)
    
    # 3) Attraper l'objet
    set_all(orange)
    grip_close()
    sleep(400)

    
    # 5) Retour vers A (même temps que l’aller + marge)
    t_back_target = t_out + RETURN_BONUS_MS
    follow_line_for_ms(t_back_target)

    # 6) Déposer l'objet à A
    set_all(green)
    grip_open()
    sleep(400)

    # Reculer légèrement pour dégager la pince
    robot.move(-30, -30, RELEASE_BACK_MS)
    robot.move(0, 0)
    set_all(white)
    display.show('A')

# ================== PROGRAMMES ==================
while True:

    if button_a.was_pressed():
        robot.move(0, 0)
        prog = (prog + 1) % 10
        display.show(prog)

    # --- prog 0: téléop basique (ton code) ---
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
            robot.goToPosition(1, 20)   # pince (fermer/ouvrir selon ton montage)
        elif msg == '1':
            robot.goToPosition(1, 160)

    # --- prog 1: suivi + stop ultrason (ton code, léger clean) ---
    if prog == 1:
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
        if msg == 'd':
            robot.move(0, 0)
        if msg == '2':
            display.scroll(distance_cm(), 50)

    if prog == 2:
        msg = radio.receive()
        if msg == 'u':
            robot.move(60,60)

    # --- prog 3: MISSION COMPLETE A→B→A avec pince, 180°, ultrason, suivi de ligne ---
    if prog == 3:
        # Commandes radio:
        #   'g' : go (lancer la mission)
        #   's' : stop d'urgence
        msg = radio.receive()
        if msg == 'd':
            robot.move(0, 0)
            set_all(red)
        elif msg == 'u':
            mission_A_to_B_pick_and_return()-
            robot.move(190,-190, 1200°)
        # Petit blink pour montrer l’attente
        blink(0, 600, 120, blue, black)
        sleep(5)
