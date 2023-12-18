from constantes import *
import json

class Information:

    def __init__(self, client, topic, message):
        self.client = client
        self.topic = topic
        self.message = message
        self.operation = self.__extraire_operation(topic)
        self.code = self.__extraire_code(topic)
        self.composant = self.__extraire_composant(topic)
        self.affichage = self.__extraire_affichage(message)
        self.son = self.__extraire_son(message)
        
    # mettre dans une liste
    def afficher(self):
        print("ANALYSE D'UN MESSAGE MQTT APRES TRAITEMENT")
        print("CLIENT    : {0}".format(self.client))
        print("TOPIC     : {0}".format(self.topic))
        print("MESSAGE   : {0}".format(self.message))
        print("OPERATION : {0}".format(self.operation))
        print("CODE      : {0}".format(self.code))
        print("COMPOSANT : {0}".format(self.composant))
        print("AFFICHAGE : {0}".format(self.affichage))
        print("SON       : {0}".format(self.son))

    def __extraire_operation(self, topic):
        if topic.find(OPERATION_STATUT) != -1:
            return OPERATION_STATUT
        if topic.find(OPERATION_COMMANDE) != -1:
            return OPERATION_COMMANDE
        raise ValueError('Operation inconnue', topic)
                
    def __extraire_code(self, topic):
        if self.operation == OPERATION_STATUT:
            return "";
        return topic[topic.index(self.operation) + len(self.operation) + 1:]

    def __extraire_composant(self, topic):    
        if topic.find(CONTROLEUR) != -1:
            return CONTROLEUR
        if topic.find(MODULE) != -1:
            return MODULE
        if topic.find(PORTAIL) != -1:
            return PORTAIL
        raise ValueError('Composant inconnu', topic, message)

    def __extraire_affichage(self, message):
        texte = json.loads(message)
        if "affichage" in texte:                
            return texte['affichage']
        return "";

    def __extraire_son(self, message):    
        texte = json.loads(message)
        if "son" in texte:
            return texte['son']
        return "";