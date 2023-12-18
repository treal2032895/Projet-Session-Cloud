from random import random
from time import time
from constantes import * 
from panneau import Panneau
from information import Information
import json
import time
import random


def protocole_01(panneau: Panneau, information: Information):
    nb = 0
    while nb<3:
        panneau.scan()
        if (panneau.getChangementBouton("btnA") == True) :
            panneau.setBtnLed_On("ledA")
        elif (panneau.getChangementBouton("btnA") == False) :
            panneau.setBtnLed_Off("ledA") 
            nb+=1    
        print(str(nb))

def protocole_02(panneau: Panneau, information: Information):

    jsonPublish("Début protocole 2", "buzzer", information)#LOG PORTAIL
    time.sleep(0.5) #SLEEP 100MS

    nb = 0
    while nb<3:
        panneau.scan()
        panneau.setRGBLed(4, (255,0,0)) #MET LED ROUGE
        nb=nb+1
        panneau.setRGBLed(5, (255,0,0))
        nb=nb+1
        panneau.setRGBLed(6, (255,0,0))
        nb=nb+1
        
    nb = 0
    while nb<3:
        panneau.scan() 
# QUAND SWITCH À ON, CHNAGE LA LED EN VERT PUIS CHNAGE L'AUTRE EN VERT AVEC LE SLEEP
        if(panneau.getChangementSwitch("switchA") == True) :
            panneau.setRGBLed(4, (34,139,34))           
            panneau.setRGBLed(8, (255,0,0))
            time.sleep(1)
            panneau.setRGBLed(8, (34,139,34))
            jsonPublish("Étape #1 complété", "", information)
            nb=nb+1

        if(panneau.getChangementSwitch("switchB")== True) :
            panneau.setRGBLed(5, (34,139,34))
            panneau.setRGBLed(9, (255,0,0))
            time.sleep(1)
            panneau.setRGBLed(9, (34,139,34))
            jsonPublish("Étape #2 complété", "", information)
            nb=nb+1

        if(panneau.getChangementSwitch("switchC")== True) :
            panneau.setRGBLed(6, (34,139,34))
            panneau.setRGBLed(10, (255,0,0))
            time.sleep(1)
            panneau.setRGBLed(10, (34,139,34))
            jsonPublish("Étape #3 complété", "", information)
            nb=nb+1
    nb=0
#BOUTON DANGER EN ROUGE PUIS APRÈS APPUIE, EN VERT
    while nb<1:
        panneau.scan()
        panneau.setRGBLed(7, (255,0,0))

        if (panneau.getChangementBouton("btnD") == True) :
            panneau.setRGBLed(7, (34,139,34))
            nb=1

    jsonPublish("Fin protocole 2", "boom", information)
    print("fin du procotole 2")

def protocole_03(panneau: Panneau, information: Information):

    jsonPublish("Début protocole 3", "buzzer", information)
    panneau.scan()
    panneau.setJauge(0)
    nb=0
    jauge=0

    while nb<3:
        panneau.scan()
        #A CHAQUE COUP À DROITE, AUGMENTE LE JAUGE DE 10%
        if(panneau.getChangementRotatif() == 5) :
               jauge=jauge+10
               panneau.setJauge(jauge)
               jsonPublish("À droite !", "", information)
        #A CHAQUE COUP À GAUCHE, DIMINUE LE JAUGE DE 10%
        if(panneau.getChangementRotatif() == 6) :
               jauge=jauge-10
               panneau.setJauge(jauge)
               jsonPublish("À gauche !", "", information)
        #LORS DE L'APPUIE BTN ROTATIF, VÉRIFIE LE % DE LA JAUGE ET AFFICHE LA BONNE COULEUR
        if(panneau.getChangementBouton("Rotatif_btn") == 1):
            if(jauge>=30):
                  panneau.setRGBLed(0, (34,139,34))
                  jsonPublish("En vert !", "", information)
                  nb=nb+1

            if(jauge>=60):
                  panneau.setRGBLed(0, (255,255,0))
                  jsonPublish("En jaune !", "", information)
                  nb=nb+1

            if(jauge>=90):
                  panneau.setRGBLed(0, (255,165,0))
                  jsonPublish("En orange ! !", "", information)
                  nb=nb+1
                  
            if(jauge>=100):
                  panneau.setRGBLed(0, (255,0,0))
                  jsonPublish("EN ROUGE !", "", information)
                  nb=nb+1




    jsonPublish("Fin protocole 3", "boom", information)
    print("fin du protocole 3")

def protocole_04(panneau: Panneau, information: Information):

    print("P04 terminé")


def jsonPublish(affichage, son, information : Information ):
    send_msg = {
        'affichage' : affichage,
        'son'       : son
    }
    information.client.publish("CLOUD/ATMAB/MODULE/STATUT/CMD/" + information.code, json.dumps(send_msg))