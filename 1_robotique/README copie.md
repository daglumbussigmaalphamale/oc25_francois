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
