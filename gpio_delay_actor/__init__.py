# -*- coding: utf-8 -*-
import time

from modules import cbpi
from modules.core.hardware import ActorBase
from modules.core.props import Property

try:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
except Exception as e:
    print(e)
    pass


@cbpi.actor
class GPIODelay(ActorBase):

    def __init__(self):
        self.gpio = Property.Select("GPIO", options=range(28),
                           description="GPIO pin number")
        self.delay = Property.Number(
            "Minimum delay",
            configurable=True,
            default_value=300,
            unit="s",
            description="Minimum wait time before switching on (s)",
        )
        self.switched_off_at = None
        gpio = int(self.gpio)
        GPIO.setup(gpio, GPIO.OUT)
        GPIO.output(gpio, 0)

    def on(self, power=0):
        gpio = int(self.gpio)
        cbpi.app.logger.info("Request to switch on GPIO %d" % gpio)
        if GPIO.input(gpio) == 1:
            cbpi.app.logger.info("GPIO %d already on" % gpio)
            return

        if self.switched_off_at is not None:
            since_last_off = time.time() - self.switched_off_at
            cbpi.app.logger.info(
                "GPIO %d last switched off %d seconds ago" %
                (gpio, since_last_off)
            )

            if since_last_off < float(self.delay):
                cbpi.app.logger.info(
                    "Not enough time since last switched off GPIO %d" % gpio
                )
                return

        cbpi.app.logger.info("Switching on GPIO %d" % gpio)
        GPIO.output(gpio, 1)

    def off(self):
        gpio = int(self.gpio)
        cbpi.app.logger.info("Request to switch off GPIO %d" % gpio)
        if GPIO.input(gpio) == 0:
            cbpi.app.logger.info("GPIO already off %d" % gpio)
            return

        cbpi.app.logger.info("Switching off GPIO %d" % gpio)
        self.switched_off_at = time.time()
        GPIO.output(gpio, 0)
