from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_display_text import wrap_text_to_lines
from audiocore import WaveFile
import board
import displayio
import time
from constantes import *

try:
    from audioio import AudioOut
except ImportError:
    try:
        from audiopwmio import PWMAudioOut as AudioOut
    except ImportError:
        pass  # not always supported by every board!


class Interface():
    # ------------------
    # Méthodes privées
    # ------------------

    # Constructeur
    def __init__(self, nomFusee = "", debug = False):
        # Attributs
        self.__DEBUG = debug
        self.__NOM_FUSEE = nomFusee
        self.__messages = ["", "", "", "", "", "", "", ""]
        self.__audio = AudioOut(board.A0)
        self.__display = board.DISPLAY

        self.__journaliser("Initialisation")

        self.__charger_polices()
        self.__charger_ecran_initialisation()
        self.__charger_ecran_principal()

        # Affichage de l'écran d'initialisation
        self.__display.show(self.__ecranInit)

    def __charger_ecran_initialisation(self):
        self.__journaliser("Chargement de l'écran d'initialisation")
        self.__ecranInit = displayio.Group()
        logoFull = displayio.OnDiskBitmap(IMAGE_INIT)
        logoFull_sprite = displayio.TileGrid(logoFull, pixel_shader=getattr(logoFull, 'pixel_shader', displayio.ColorConverter()))

        self.__ecranInit.append(logoFull_sprite)

        self.__init_label = Label(self.__fontLarge, text=INIT_PORTAIL, color=0xFFFFFF)
        self.__init_label.x = 8
        self.__init_label.y = 20
        self.__ecranInit.append(self.__init_label)

        self.__wifi_label = Label(self.__fontMedium, text=INIT_WIFI, color=0x888888)
        self.__wifi_label.x = 8
        self.__wifi_label.y = 270
        self.__ecranInit.append(self.__wifi_label)

        self.__mqtt_label = Label(self.__fontMedium, text=INIT_MQTT, color=0x888888)
        self.__mqtt_label.x = 8
        self.__mqtt_label.y = 300
        self.__ecranInit.append(self.__mqtt_label)

    def __charger_ecran_principal(self):
        self.__journaliser("Chargement de l'écran principal")
        self.__ecranPrinc = displayio.Group()
        entete = displayio.OnDiskBitmap(IMAGE_ENTETE)
        entete_sprite = displayio.TileGrid(entete, pixel_shader=getattr(entete, 'pixel_shader', displayio.ColorConverter()))

        self.__ecranPrinc.append(entete_sprite)

        self.__fusee_label = Label(self.__fontLarge, text=self.__NOM_FUSEE, color=0xFFFFFF)
        self.__fusee_label.x = 120
        self.__fusee_label.y = 42
        self.__ecranPrinc.append(self.__fusee_label)

        self.__messages_label = Label(self.__fontSmall, text="", color=0xDDDDDD)
        self.__messages_label.x = 8
        self.__messages_label.y = 120
        self.__ecranPrinc.append(self.__messages_label)

    def __charger_polices(self):
        self.__journaliser("Chargement des polices de caractères...")
        self.__fontLarge = bitmap_font.load_font(FONT_LARGE)
        self.__fontLarge.load_glyphs(GLYPHS)
        self.__fontMedium = bitmap_font.load_font(FONT_MEDIUM)
        #self.__fontMedium.load_glyphs(GLYPHS)
        self.__fontSmall = bitmap_font.load_font(FONT_SMALL)
        self.__fontSmall.load_glyphs(GLYPHS)

    #
    # Définis la luminosité de l'écran - Pas utilisée pour le moment
    #
    def __set_backlight(self, val):
        val = max(0, min(1.0, val))
        self.__display.auto_brightness = False
        self.__display.brightness = val

    def __journaliser(self, message):
        print ("[Interface] " + message)
        

    # ------------------
    # Méthodes publiques
    # ------------------

    #
    # Ajoute une ligne à l'écran et fait défiler les autres vers le bas
    # Conserve 6 lignes à l'écran
    #
    def afficher(self, message):
        # Vide le label des messages
        self.__messages_label.text = ""

        if (self.__DEBUG):
            self.__journaliser("Affiche : " + message)

        # Efface le dernier message et insère le nouveau message au début
        self.__messages.pop(5)
        self.__messages.insert(0, message)

        # Remplit le label des messages
        for x in range (0, 6):
            self.__messages_label.text = self.__messages_label.text + self.__messages[x] + "\n"

    def effacer(self):
        self.__messages.clear()
        
    
    #
    # Fait jouer un son WAV. Le nom du fichier est envoyé en paramètre (sans l'extension)
    # Format des fichiers: WAV, 16 Bit, 22 KHz sample rate (ou moins)
    def jouerSon(self, fichier = ""):
        if (self.__DEBUG):
            self.__journaliser("Jouer un son : " + fichier)

        try :
            wave_file = open(PATH_SON + fichier + ".wav", "rb")
            wave = WaveFile(wave_file)

            self.__audio.play(wave)

            while(self.__audio.playing):
                pass
        except:
            if (self.__DEBUG):
                self.__journaliser("ERREUR - Incapable de jouer le son!")


    # Change l'indicateur de Wifi dans l'écran d'initialisation'
    def setWIFI_ok(self):
        self.__wifi_label.text = INIT_WIFI_OK
        self.__wifi_label.color = 0x00FF00

    #
    # Change l'indicateur de MQTT dans l'écran d'initialisation
    # et déclenche l'affichage de l'écran principal
    def setMQTT_ok(self):
        self.__journaliser("Initialisation MQTT OK!")
        self.__mqtt_label.text = INIT_MQTT_OK
        self.__mqtt_label.color = 0x00FF00
        time.sleep(1.5)
        self.__ecranInit = None
        self.__display.show(self.__ecranPrinc)