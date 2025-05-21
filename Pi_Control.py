import RPi.GPIO as GPIO
import time


def pin_setup(pin=18):
    """
    Setup the GPIO pins.
    """
    # Set up GPIO
    GPIO.setwarnings(False)
    GPIO.cleanup()

    # Use Broadcom pin numbering
    GPIO.setmode(GPIO.BCM)

    # Pin 18 as output
    LED_PIN = pin
    GPIO.setup(LED_PIN, GPIO.OUT)


def sendsignal(pin=18):
    """
    Send a signal to the GPIO pin.
    """
    # Pin 18 as output
    LED_PIN = pin

    # Blink the LED
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(LED_PIN, GPIO.LOW)
    
def cleanup(pin=18):
    """
    Cleanup the GPIO pins.
    """
    # Pin 18 as output
    LED_PIN = pin

    # Cleanup GPIO
    GPIO.cleanup(LED_PIN)
    
def drop_power(pin=18):
    """
    Executes the routine to send a signal to the relay to drop power.
    """
