from machine import Pin, ADC
from utime import sleep_ms
from fifo import Fifo
import micropython

micropython.alloc_emergency_exception_buf(200)


class InterruptSignal:
    def __init__(self, signal_pin, fifo):
        self.button = Pin(signal_pin, Pin.IN)
        self.fifo = fifo
        self.nr = signal_pin

        self.button.irq(
            handler=self._handler, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, hard=True
        )

    def _handler(self, pin):
        self.fifo.put(self.nr)


# Shared FIFO
events = Fifo(30)

# ADC input: GP26
adc = ADC(26)

# Button input: GP12
button = InterruptSignal(12, events)

# Initial digital value
prev_value = button.button.value()

print("Program started")

while True:

    if events.has_data():

        event = events.get()

        current_value = button.button.value()

        adc_value = adc.read_u16()
        voltage = (adc_value / 65535) * 3.3

        if current_value == 1 and prev_value == 0:

            print("Triggered High")
            print("ADC Voltage:", round(voltage, 3), "V")

            prev_value = 1

        elif current_value == 0 and prev_value == 1:

            print("Triggered Low")
            print("ADC Voltage:", round(voltage, 3), "V")

            prev_value = 0

    sleep_ms(1)
