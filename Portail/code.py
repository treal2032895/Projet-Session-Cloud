# ================================= #
#    IMPORTATION DES LIBRAIRIES
# ================================= #
import board
import displayio
import busio
import json
from digitalio import DigitalInOut
import neopixel
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import time
import supervisor
from constantes import *
from information import *
from interface import *


# ======================================== #
#     ACTIVATION DE L'INTERFACE
# ======================================== #
interface = Interface(FUSEE, debug = False)

# ================================= #
#       FICHIER DE PARAMÈTRES
# ================================= #
try:
    from secrets import secrets
except ImportError:
    print("Veuillez définir les paramètres dans le fichier secrets.py")
    raise

# ================================= #
#              ESP32
# ================================= #
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

# ================================= #
#                RGB LED
# ================================= #
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)


# ================================= #
#                WIFI
# ================================= #
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

# Poue deboggage, affiche les réseaux disponibles
for ap in esp.scan_networks():
    print("\t%s\t\tRSSI: %d" % (str(ap["ssid"], "utf-8"), ap["rssi"]))

# ================================= #
#              ÉCRAN
# ================================= #
display = board.DISPLAY

def set_backlight(val):
    val = max(0, min(1.0, val))
    board.DISPLAY.auto_brightness = False
    board.DISPLAY.brightness = val
    
# ======================================== #
#     CONNEXION AU WIFI ET SERVEUR MQTT
# ======================================== #

print("Connexion au WiFi...")

try:
    wifi.connect()
except Error as e:
    print("Problème de connection: ", e)
print("WiFi OK!")

interface.setWIFI_ok()
print("WiFi OK!")

MQTT.set_socket(socket, esp)

if (secrets["mqtt_user"] != ""):
    mqtt_client = MQTT.MQTT(
        broker=secrets["mqtt_broker"],
        port=secrets["mqtt_port"],
        username=secrets["mqtt_user"],
        password=secrets["mqtt_pass"],
    )
else:
    mqtt_client = MQTT.MQTT(
        broker=secrets["mqtt_broker"],
        port=secrets["mqtt_port"],
    )

# ================================= #
#         CALLBACK MQTT
# ================================= #

def connected(client, userdata, flags, rc):
    interface.setMQTT_ok()
    print("Serveur:\t%s" % secrets["mqtt_broker"])
    print("\nAbonnement au topic...")
    # TODO
    mqtt_client.subscribe(TOPIC_STATUT)
    print("\nLe portail est fonctionnel...")
    # TODO
    mqtt_client.subscribe(TOPIC_CMD)
    mqtt_client.publish(TOPIC_PORTAIL, "ON")

    


   
    
def disconnected(client, userdata, rc):
    print("Déconnecté du serveur!")

def subscribe(mqtt_client, userdata, topic, granted_qos):
    print("Abonnement au topic:\t{0}\tQOS level: {1}".format(topic, granted_qos))

def unsubscribe(mqtt_client, userdata, topic, pid):
    print("Désabonnement du topic {0} avec le PID {1}".format(topic, pid))

def publish(mqtt_client, userdata, topic, pid):
    print("Message publié sur {0} avec PID {1}".format(topic, pid))

def message(client, topic, message):
    #interface.afficher("TOPIC   "+str(topic))
    #interface.afficher("MESSAGE "+str(message))
    info = Information(client, topic, message)
    info.afficher()
    interface.afficher(info.affichage)
    interface.jouerSon(info.son)
       
    
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message
mqtt_client.on_subscribe = subscribe
mqtt_client.on_unsubscribe = unsubscribe
mqtt_client.on_publish = publish

print("Connexion au serveur MQTT %s" % mqtt_client.broker)
mqtt_client.connect()

# ================================= #
#        BOUCLE PRINCIPALE
# ================================= #

while True:
    try:
        mqtt_client.loop()
    except:
            # Reboot, incapable de gérer la reconnexion à MQTT autrement
        supervisor.reload()
    
    time.sleep(0.1)