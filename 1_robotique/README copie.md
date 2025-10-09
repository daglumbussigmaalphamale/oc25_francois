# oc25_francois
---
why did I consipicuously choose computer science?
---
The CS teacher gave us a very intriguing introduction to his cursus.(日本が好き)

---
TESTE OBJECTIFS
---
- faire un parcours d'un point A à B
- de suivre une ligne
- de détecter vers un objet avec capteur ultrason
- tourner de 180deg
- va attraper l'objet avec la pince
- va ramenez l'objet à la position A


Partie libre
--
exemples: une dance, un lightshow, de la musique, fight, etc...
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡄⠒⠂⢴⡢⢠⡀⢀⡀⣀⢰⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀

## Partie Pratique

Pour réaliser notre travail, nous avons décider de réaliser plusieurs variables, pour ensuite avoir un code, dans lequel il suffisait de les rappeler.

Pour commencer, nous avons utiliser un code que nous avions déjà utilisé dans des TP précédents, pour gagner un peu de temps.
### Constantes
Ensuite nous avons définit les constantes suivantes:
```python
BACK_OFF_CM = 8                 # recul avant de tourner 
FORWARD_SEARCH_TIMEOUT_MS = 5000 # combien de temps on avance pour retrouver l'objet après le 180

# Distance/temps pour avancer (cm -> ms)
D_CAL_CM_PER_SLOW = 10.3  # utilisé par la fonction avancer()

# Conversion angle -> ms pour pivoter
TURN_CAL_1000MS_PER_140DEG = 1000  # déjà dans la fonction tourner(a)

# Suivi de ligne
LINE_SPEED = 20          # vitesse de base en suivi
LINE_K = 0.08            # gain correcteur (plus grand = plus réactif)

# Ultrason
DIST_THRESH_PICK = 6    # seuil (cm) pour considérer l'objet atteint
DIST_APPROACH_MAX = 40   # distance (cm) max à laquelle on commence l'approche lente

# Pince 
GRIP_OPEN = 160
GRIP_CLOSED = 20

# Sécurités/délais
APPROACH_SPEED = 20
RETURN_BONUS_MS = 400    # marge au retour vs durée aller (ms)
RELEASE_BACK_MS = 600    # petit recul après dépose (ms)
```
Cela facilite ensuite, le fonctionnement des variables, en ayant déjà certaines valeurs fixes.

### Variables
Ensuite, nous avons commencer par définir une fonction qui permet de faire fonctionner le capteur à ultrason, dans le but de détecter des objets, qui se trouveraient devant le robot.
```python
def distance_cm():
    trigger.write_digital(1)
    trigger.write_digital(0)
    distance = time_pulse_us(echo,1)/2e6*340
    return max(0, min(400, round(distance*100)))
```

Nous avons ensuite créé une variable qui permet de colorer les LED du robot de manière différente, à chaque moment de la mission A-->B
```python
def set_all(color):
    for i in range(4):
        np[i] = color
    np.show()
```

Nous avons fait une variable qui permet d'ouvrir la pince
```python
def grip_open():
    robot.goToPosition(1, GRIP_OPEN)
```
Et une pour la fermer
```python
def grip_close():
    robot.goToPosition(1, GRIP_CLOSED)
```
Ensuite nous avons définit une variable, qui permet de suivre une ligne, grâce aux capteurs infrarouges, qui se situent en dessous de lui.
```python
def follow_line_step(base=LINE_SPEED, k=LINE_K):
    left = pin1.read_analog()
    right = pin2.read_analog()
    # erreur: positif si la ligne est plus à droite (right < left)
    error = (left - right)
    correction = int(k * error)
    # limite les vitesses
    l = max(-100, min(100, base - correction))
    r = max(-100, min(100, base + correction))
    robot.move(l, r)
```

### Assemblage variable

Nous avons, ensuite assembler plusieurs variables pour en définir d'autre plus précises et qui permettent au robot de réaliser une partie complète de la mission.

Premierement, nous avons fait une variable qui permet de suivre une ligne jusqu'à ce que le robot détecte un objet. Nous avons inclus la notion de temps pour que le robot puisse revenir approximativement à la même place une fois le travail effectué.
```python
def follow_line_until_object(dist_thresh=DIST_THRESH_PICK, max_ms=30000):
    set_all(blue)  # suivi A→B
    t0 = running_time()
    while running_time() - t0 < max_ms:
        d = distance_cm()
        if d <= DIST_APPROACH_MAX:
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
```

Ensuite nous avons fait une variable qui permet au robot d'approcher l'objet, une fois qu'il l'à détecté.
```python
def approach_until(dist_thresh=DIST_THRESH_PICK):
    set_all(cyan)
    while True:
        d = distance_cm()
        if 0 < d <= dist_thresh:
            robot.move(0, 0)
            return True
        robot.move(APPROACH_SPEED, APPROACH_SPEED)
        sleep(10)
```

Puis une variable pour qu'il se retourne
```python
def turn_180():
    set_all(magenta)
    tourner(180)
    robot.move(0, 0)
```

Et enfin, pour qu'il retourne à son point initial en suivant un tracé
```python
def follow_line_for_ms(duration_ms):
    set_all(yellow)  # retour B→A
    t0 = running_time()
    while running_time() - t0 < duration_ms:
        follow_line_step(base=LINE_SPEED)
        sleep(5)
    robot.move(0, 0)
```

### Code global

Finalement, nous avons tout mis ensemble pour définir une seule variable qui réalise l'entier du travail.
```python
def mission_A_to_B_pick_and_return():
    
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

    
    # 5) Retour vers A 
    set_all(blue)
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
```

### Code pour la télécommande

Finalement, nous avons mis un code final que nous avons attribuer à l'une des variable de la télécommande
```python
 if prog == 3:
        msg = radio.receive()
        if msg == 'd':
            robot.move(0, 0)
            set_all(red)
        elif msg == 'u':
            mission_A_to_B_pick_and_return()
        # Petit blink pour montrer l’attente
        blink(0, 600, 120, blue, black)
        sleep(5)
```
