import board
import rotaryio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_motor import stepper
import adafruit_aw9523
import neopixel
import time

# Constantes pour les états (pas d'énum en circuitpython)
APPUYER  = 1
RELACHER = 2
ACTIF    = 3
INACTIF  = 4
DROITE   = 5
GAUCHE   = 6

class Panneau():
    # Méthodes privées

    def __init__(self, debug = False):
        print ("------------------------------------------")
        print ("[Panneau]  Initialisation...")
        print ("")

        self.__btnLedsPins = {
            "ledA" : 1,
            "ledB" : 2,
            "ledC" : 3,
            "ledD" : 4
        }
        self.__debug = debug

        self.rainbow = True

        # Instanciation des composantes
        self.__btnRotatif = Encodeur(board.A1, board.A2, board.A3)

        self.__btnA = Bouton(board.D6)
        self.__btnB = Bouton(board.D7)
        self.__btnC = Bouton(board.D8)
        self.__btnD = Bouton(board.D9)

        self.__switchA = Switch(board.D12)
        self.__switchB = Switch(board.D11)
        self.__switchC = Switch(board.D10)

        self.__jauge = Stepper(board.D2, board.D3, board.D4, board.D5)
        self.__jauge.__zero()
        if (self.__debug):
            print ("[Jauge] Remise à zéro")

        self.__ledsRGB = NeoPixels(board.D13)

        self.__btnLeds = BtnLeds()

        self.__initEtats()

        # Animation des LEDS RGB
        if (self.rainbow):
            self.__ledsRGB.__rainbow_cycle(0.0005)
            self.__ledsRGB.__off()

        print ("[Panneau]  Initialisation OK!")
        print ("------------------------------------------")


    # Méthodes privées

    def __initEtats(self):
        self.__etats = {
            "Rotatif"       : None,
            "Rotatif_btn"   : None,
            "btnA"          : None,
            "btnB"          : None,
            "btnC"          : None,
            "btnD"          : None,
            "switchA"       : None,
            "switchB"       : None,
            "switchC"       : None
        }


    # Méthodes publiques
    def getChangement(self, composant):
        return self.__etats[composant]


    def getChangementRotatif(self):
        return self.__etats["Rotatif"]


    def getChangementBouton(self, composant):
        if not (self.__etats[composant]) is None :
            if (self.__etats[composant] == APPUYER):
                return True
            else:
                return False

    def getChangementSwitch(self, composant):
        if not (self.__etats[composant]) is None :
            if (self.__etats[composant] == ACTIF):
                return True
            else:
                return False

    def getEtatJauge(self):
        return self.__jauge.valeur

    def setJauge(self, valeur):
        if (self.__jauge.__set(valeur) == True):
            if (self.__debug): 
                print("[Jauge] : {}%".format(valeur))


    def setRGBLed(self, led, couleur):
        self.__ledsRGB.__set(led, couleur)

    def setRGBLedsOff(self):
        self.rainbow = False
        self.__ledsRGB.__off()

    def setBtnLed_Toggle(self, led):
        self.__btnLeds.__toggle(self.__btnLedsPins[led])

    def setBtnLed_On(self, led):
        self.__btnLeds.__on(self.__btnLedsPins[led])

    def setBtnLed_Off(self, led):
        self.__btnLeds.__off(self.__btnLedsPins[led])

    def scan(self):
        #Réinitialisation des états
        self.__initEtats()

        #Scan de l'encodeur
        tmp = self.__btnRotatif.__scan()
        if not tmp[0] is None:
            if (self.__debug): 
                print ("[Encodeur]  {}".format(tmp[0]))
            self.__etats["Rotatif"] = tmp[0]
        if not tmp[1] is None:
            self.__etats["Rotatif_btn"] = tmp[1]
            if (self.__debug):
                print ("[Encodeur (Bouton)]  {}".format(tmp[1]))

        #Scan des boutons
        tmp = self.__btnA.__scan()
        if not tmp is None:
            self.__etats["btnA"] = tmp
            if (self.__debug): 
                print ("[Bouton A (Jaune)]  {}".format(tmp))

        tmp = self.__btnB.__scan()
        if not tmp is None:
            self.__etats["btnB"] = tmp
            if (self.__debug): 
                print ("[Bouton B (Jaune)]  {}".format(tmp))

        tmp = self.__btnC.__scan()
        if not tmp is None:
            self.__etats["btnC"] = tmp
            if (self.__debug): 
                print ("[Bouton C (Jaune)]  {}".format(tmp))

        tmp = self.__btnD.__scan()
        if not tmp is None:
            self.__etats["btnD"] = tmp
            if (self.__debug): 
                print ("[Bouton D (Rouge)]  {}".format(tmp))

        #Scan des switches
        tmp = self.__switchA.__scan()
        if not tmp is None:
            self.__etats["switchA"] = tmp
            if (self.__debug): 
                print ("[Switch A]  {}".format(tmp))

        tmp = self.__switchB.__scan()
        if not tmp is None:
            self.__etats["switchB"] = tmp
            if (self.__debug): 
                print ("[Switch B]  {}".format(tmp))
        
        tmp = self.__switchC.__scan()
        if not tmp is None:
            self.__etats["switchC"] = tmp
            if (self.__debug): 
                print ("[Switch C]  {}".format(tmp))




class Encodeur():

    # Méthodes privées

    def __init__(self, pinEncA, pinEncB, pinBtn):
        self.__encoder = rotaryio.IncrementalEncoder(pinEncA, pinEncB)
        self.__prevPosEncoder = 0

        self.__btn = DigitalInOut(pinBtn)
        self.__btn.direction = Direction.INPUT
        self.__btn.pull = Pull.UP
        self.__prevStateBtn = self.__btn.value


    def __scan(self):
        tmpPos = self.__encoder.position
        retEnc = None
        if tmpPos != self.__prevPosEncoder:
            #Debug: Affiche la position actuelle de l'encodeur, relativement à sa position à la création de l'objet (0)
            #print(self.tmpPos)
            if self.__prevPosEncoder < tmpPos:
                retEnc = DROITE
            else:
                retEnc = GAUCHE
        self.__prevPosEncoder = tmpPos

        tmpValue = self.__btn.value
        retBtn = None
        
        if tmpValue != self.__prevStateBtn:
            if not tmpValue:
                retBtn = APPUYER
            else:
                retBtn = RELACHER
        self.__prevStateBtn = tmpValue

        return(retEnc, retBtn)



class Bouton():

    # Méthodes privées
    def __init__(self, pin):
        self.btn = DigitalInOut(pin)
        self.btn.direction = Direction.INPUT
        self.btn.pull = Pull.UP
        self.prevStateBtn = self.btn.value
        self.ret = None


    def __scan(self):
        self.tmpValue = self.btn.value
        self.ret = None

        if self.tmpValue != self.prevStateBtn:
            if not self.tmpValue:
                self.ret = APPUYER
            else:
                self.ret = RELACHER
        self.prevStateBtn = self.tmpValue

        return(self.ret)



class Switch():
    # Méthodes privées

    def __init__(self, pin):
        self.btn = DigitalInOut(pin)
        self.btn.direction = Direction.INPUT
        self.btn.pull = Pull.DOWN
        self.prevStateBtn = self.btn.value
        self.ret = None


    def __scan(self):
        self.tmpValue = self.btn.value
        self.ret = None

        if self.tmpValue != self.prevStateBtn:
            if self.tmpValue:
                self.ret = ACTIF
            else:
                self.ret = INACTIF
        self.prevStateBtn = self.tmpValue

        return(self.ret)



class Stepper():
    def __init__(self, pinA, pinB, pinC, pinD):
        self.DELAIS = 0.01
        self.STEPS = 600
        self.valeur = 0

        self.coils = (
            DigitalInOut(pinA),
            DigitalInOut(pinB),
            DigitalInOut(pinC),
            DigitalInOut(pinD),
        )

        for self.coil in self.coils:
            self.coil.direction = Direction.OUTPUT

        self.motor = stepper.StepperMotor(self.coils[0], self.coils[1], self.coils[2], self.coils[3], microsteps=None)

        #print ("[Jauge] : Remise à zéro DÉSACTIVÉE")


    def __zero(self):
        for self.step in range(0, self.STEPS):
            self.motor.onestep(direction=stepper.BACKWARD)
            time.sleep(self.DELAIS)

        self.valeur = 0


    def __set(self, valeur):
        if (valeur >= 0 and valeur <= 100):
            if (valeur > self.valeur):
                direction=stepper.FORWARD
                deplacement = valeur - self.valeur
            else:
                direction=stepper.BACKWARD
                deplacement = self.valeur - valeur

            for self.step in range(0, deplacement * 6):
                self.motor.onestep(direction = direction)
                time.sleep(self.DELAIS)

            self.valeur = valeur
            return True



class NeoPixels():
    def __init__(self, pin):
        self.__NBPIXELS = 20
        __ORDRE = neopixel.GRB
        #__LUMINOSITE = 0.025    # Sans diffuseur
        __LUMINOSITE = 0.2     # Avec image comme diffuseur

        self.__pixels = neopixel.NeoPixel(pin, self.__NBPIXELS, brightness=__LUMINOSITE, auto_write=False, pixel_order=__ORDRE)

        self.__pixels.fill((0, 0, 0))
        self.__pixels.show()


    def __off(self):
        self.__pixels.fill((0, 0, 0))
        self.__pixels.show()

    def __set(self, led, couleur):
        self.__pixels[led] = couleur
        self.__pixels.show()

    def __test(self):
        DELAIS = 0.5
        print("[LedsRGB] : Rouge")
        self.__pixels.fill((255, 0, 0))
        self.__pixels.show()
        time.sleep(DELAIS)

        print("[LedsRGB] : Vert")
        self.__pixels.fill((0, 255, 0))
        self.__pixels.show()
        time.sleep(DELAIS)

        print("[LedsRGB] : Bleu")
        self.__pixels.fill((0, 0, 255))
        self.__pixels.show()
        time.sleep(DELAIS)

        print("[LedsRGB] : OFF")
        self.__pixels.fill((0, 0, 0))
        self.__pixels.show()
        time.sleep(DELAIS)

    def __wheel(self, pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return (r, g, b)

    def __rainbow_cycle(self,wait):
        for j in range(0, 255):
            for i in range(self.__NBPIXELS):
                pixel_index = (i * 256 // self.__NBPIXELS) + j
                self.__pixels[i] = self.__wheel(pixel_index & 255)
            self.__pixels.show()
            time.sleep(wait)

class BtnLeds():
    def __init__(self):
        self.__i2c = board.I2C()
        self.__aw = adafruit_aw9523.AW9523(self.__i2c)
        self.__leds = [None for a in range(0, 15)]

        for x in range (0, 15):
            self.__leds[x] = self.__aw.get_pin(x)
            self.__leds[x].switch_to_output(value=False)

    def __toggle(self, led):
        self.__leds[led].value = not self.__leds[led].value

    def __on(self, led):
        self.__leds[led].value = True

    def __off(self, led):
        self.__leds[led].value = False
