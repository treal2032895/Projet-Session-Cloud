#******* MODULE *******

# Projet
PROJET = "CLOUD"
FUSEE = "ATMAB"
CONTROLEUR = "CONTROLEUR"
MODULE = "MODULE"
PORTAIL = "PORTAIL"
OPERATION_STATUT = "STATUT"
OPERATION_COMMANDE = "CMD"

# Les sons (exemples)
SON_DEMARRAGE = "boom"
SON_ENCOURS = "buzzer"
SON_FERMETURE = "cheering"
SON_ECHEC = "cheering"

#Messages
MESSAGE_DEMARRAGE_MODULE = "Demarrage du module"
MESSAGE_FERMETURE_MODULE = "Fermeture du module"
MESSAGE_DEMARRAGE_PROTOCOLE = "Demarrage du protocole"
MESSAGE_FIN_PROTOCOLE = "Fin du protocole"

# Les topics MQTT (exemples)
MQTT_TOPIC = PROJET + "/" + FUSEE
MQTT_TOPIC_MODULE_STATUT = MQTT_TOPIC + "/" + MODULE + "/" + OPERATION_STATUT


#Les fonctions (IMPORTANT)
P01 = "protocole_01"
P02 = "protocole_02"
P03 = "protocole_03"
P04 = "protocole_04"

# Topic Subscribe
TOPIC_STATUT = "CLOUD/ATMAB/MODULE/STATUT/"
TOPIC_CMD = "CLOUD/ATMAB/CONTROLEUR/CMD/#"

#Topic Publishp
TOPIC_PORTAIL = "CLOUD/ATMAB/PORTAIL/STATUT/"