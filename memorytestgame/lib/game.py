from __future__ import print_function
from lcd import Lcd
from mock import MagicMock, patch
from tinydb import TinyDB, Query
import random
import time

try:
    import RPi.GPIO as Gpio
except ImportError:
    print("[Game][error] An error occurred importing 'RPi.GPIO'")
    mock = MagicMock()
    mock.setmode.return_value = True
    mock.setup.return_value = True
    mock.add_event_detect.return_value = True
    mock.add_event_callback.return_value = True
    mock.output.return_value = True
    mock.input.return_value = True
    mock.cleanup.return_value = True
    with patch.dict('sys.modules', {'RPi': mock, 'RPi.GPIO': mock.GPIO}):
        import RPi.GPIO as Gpio


class Game:
    LEDS = None

    SWITCHES = None

    COUNTDOWN = None

    GAME_TIME = None

    FINISH_TIME = 0

    RAND = -1
    RANDS = []

    BUTTONS_STATE = False
    BUTTONS_PRESSED = []

    GAMEOVER = False

    BUTTON_ACTION_ALL = 'all'
    BUTTON_ACTION_SNAKE = 'snake'

    LEVEL = 1

    SCORE_INCREMENT = None

    gpio = None
    lcd = None
    db = None

    def __init__(self, leds, switches, countdown, game_time, score_increment):
        self.LEDS = leds
        self.SWITCHES = switches
        self.COUNTDOWN = countdown
        self.GAME_TIME = game_time
        self.SCORE_INCREMENT = score_increment

        self.gpio = Gpio
        self.lcd = Lcd()
        self.db = TinyDB('data/database.json')

        if len(self.LEDS) != len(self.SWITCHES):
            print("[Game][error] There isn't the same number of LEDS as SWITCHES")
            exit()

        try:
            self.gpio.setmode(self.gpio.BCM)

            for switch in self.SWITCHES:
                self.gpio.setup(switch, self.gpio.IN)
                self.gpio.add_event_detect(switch, self.gpio.RISING, bouncetime=300)
                self.gpio.add_event_callback(switch, self.__button_press)

            for led in self.LEDS:
                self.gpio.setup(led, self.gpio.OUT)
                self.gpio.output(led, False)
        except AttributeError:
            print("[Game][error] An error occurred initialising game")

    def start(self, run_once=False):
        print("[Game][info] Starting game")

        self.lcd.print("Press lit button", self.lcd.LINE_1)
        self.lcd.print("to start", self.lcd.LINE_2)

        try:
            self.gpio.output(self.LEDS[2], True)

            while self.gpio.input(self.SWITCHES[2]) == self.gpio.LOW:
                time.sleep(0.01)

            for led in self.LEDS:
                self.gpio.output(led, True)
        except AttributeError:
            print("[Game][error] An error occurred starting game")

        self.__countdown()
        self.__loop()
        self.finish()

        if run_once is not True:
            self.start()

    def __countdown(self):
        print("[Game][info] Starting game countdown")

        try:
            self.lcd.clear()

            for i in range(self.COUNTDOWN, -1, -1):
                if i == 0:
                    self.lcd.print("Go Go Go!", self.lcd.LINE_1)
                elif i == self.COUNTDOWN:
                    self.lcd.print("Starting in %d!" % i, self.lcd.LINE_1)
                else:
                    self.lcd.print("%d!" % i, self.lcd.LINE_1)

                time.sleep(1)

                self.gpio.output(self.LEDS[(i - 1)], False)

            self.lcd.clear()
        except AttributeError:
            print("[Game][error] An error occurred starting game countdown")

    def __loop(self):
        print("[Game][info] Starting game loop")

        self.FINISH_TIME = time.time() + (self.GAME_TIME + 1)

        try:
            while time.time() < self.FINISH_TIME and self.GAMEOVER is not True:
                print("[Game][info] Game loop iteration")

                self.BUTTONS_STATE = False
                self.BUTTONS_PRESSED = []

                for i in range(self.LEVEL):
                    self.print_information("Repeat following")

                    if len(self.RANDS) >= (i + 1):
                        self.RAND = self.SWITCHES.index(self.RANDS[i])
                    else:
                        self.RAND = random.randint(0, (len(self.LEDS) - 1))                    
                        self.RANDS.append(self.SWITCHES[self.RAND])

                    print("[Game][info] Activating button: %s" % (self.SWITCHES[self.RAND]))

                    self.gpio.output(self.LEDS[self.RAND], True)
                    time.sleep(0.5)
                    self.gpio.output(self.LEDS[self.RAND], False)

                start = time.time()

                print("[Game][info] Waiting for button press")

                while len(self.BUTTONS_PRESSED) < self.LEVEL:
                    self.print_information()

                    if time.time() >= self.FINISH_TIME:
                        break

                end = time.time()
                time_taken = end - start

                time.sleep(0.5)

                print("[Game][info] Button presses time taken: %f" % time_taken)

                if time.time() < self.FINISH_TIME:
                    if self.BUTTONS_STATE is True:
                        print("[Game][info] Level increased by %d" % 1)

                        self.LEVEL += 1
                    else:
                        self.GAMEOVER = True
        except AttributeError:
            print("[Game][error] An error occurred during game loop")

    def __button_press(self, channel):
        print("[Game][info] Button pressed: %d" % channel)

        if len(self.RANDS) == 0:
            return

        self.BUTTONS_PRESSED.append(channel)

        if len(self.BUTTONS_PRESSED) <= len(self.RANDS) and channel == self.RANDS[(len(self.BUTTONS_PRESSED) - 1)]:
            self.BUTTONS_STATE = True
        else:
            self.BUTTONS_STATE = False

    def get_score(self):
        print("[Game][info] Calculating score")

        level = self.LEVEL - 1

        if level < 1:
            return 0

        return (level * (level + 1) / level) * self.SCORE_INCREMENT

    def print_information(self, message=None):
        print("[Game][info] Printing information")

        score = self.get_score()
        remaining = int(self.FINISH_TIME - time.time())

        try:
            self.lcd.print("Remaining: %ds" % remaining, self.lcd.LINE_1)

            if message is None:
                self.lcd.print("Score: %d" % score, self.lcd.LINE_2)
            else:
                self.lcd.print(message, self.lcd.LINE_2)
        except AttributeError:
            print("[Game][error] An error occurred printing information")

    def print_score(self, high_score=False):
        print("[Game][info] Printing score")

        score = self.get_score()

        try:
            if high_score:
                self.lcd.print("High score: %d!" % self.get_score(), self.lcd.LINE_1)
                self.flash_buttons(self.BUTTON_ACTION_ALL)
                time.sleep(3)
            else:
                self.lcd.print("Your score: %d" % score, self.lcd.LINE_1)
                time.sleep(3)
        except AttributeError:
            print("[Game][error] An error occurred printing score")

    def flash_buttons(self, action):
        print("[Game][info] Flashing buttons '%s'" % action)

        try:
            if action == self.BUTTON_ACTION_SNAKE:
                for x in range(0, 4):
                    for y in range(0, len(self.LEDS)):
                        self.gpio.output(self.LEDS[y], True)
                        time.sleep(0.2)
                        self.gpio.output(self.LEDS[y], False)
            elif action == self.BUTTON_ACTION_ALL:
                for x in range(0, 4):
                    for y in range(0, len(self.LEDS)):
                        self.gpio.output(self.LEDS[y], True)

                    time.sleep(0.2)

                    for y in range(0, len(self.LEDS)):
                        self.gpio.output(self.LEDS[y], False)

                    time.sleep(0.2)
        except AttributeError:
            print("[Game][error] An error occurred flashing buttons")

    def finish(self):
        print("[Game][info] Finishing game")

        score = self.get_score()

        self.lcd.clear()

        if self.db.contains(Query().score >= score):
            self.print_score()
        else:
            self.print_score(True)

        self.db.insert({'score': score})
        self.reset()

    def reset(self):
        print("[Game][info] Resetting game")

        self.GAMEOVER = False
        self.RAND = -1
        self.RANDS = []
        self.LEVEL = 1
        self.FINISH_TIME = 0
        self.BUTTONS_STATE = False
        self.BUTTONS_PRESSED = []
        self.flash_buttons(self.BUTTON_ACTION_SNAKE)
        self.lcd.clear()

    def cleanup(self):
        print("[Lcd][info] Game clean up")

        try:
            self.gpio.cleanup()
            self.lcd.cleanup()
        except AttributeError:
            print("[Game][error] An error occurred cleaning up")

    def __exit__(self):
        print("[Game][info] Game exit")

        self.cleanup()
