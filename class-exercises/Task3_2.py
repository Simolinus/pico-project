from machine import Pin, I2C
from fifo import Fifo
from ssd1306 import SSD1306_I2C
from utime import ticks_ms, ticks_diff, ticks_add, sleep_ms
import micropython

micropython.alloc_emergency_exception_buf(200)


# Encoder interrupt class


class Encoder:

    def __init__(self, rot_a, rot_b, button_pin, fifo):

        self.button_locked = False

        self.a = Pin(rot_a, Pin.IN, Pin.PULL_UP)
        self.b = Pin(rot_b, Pin.IN, Pin.PULL_UP)
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_UP)

        self.fifo = fifo

        # Button debounce timestamp
        self.last_press = ticks_add(ticks_ms(), -51)

        # Rotary debounce timestamp
        self.last_turn = ticks_add(ticks_ms(), -5)

        # Interrupt for encoder rotation
        self.a.irq(handler=self.turn_handler, trigger=Pin.IRQ_RISING, hard=True)

        # Interrupt for button press and release
        self.button.irq(
            handler=self.button_handler,
            trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
            hard=True,
        )

    def turn_handler(self, pin):

        current_time = ticks_ms()

        # Small filter to prevent multiple signals per turn
        if ticks_diff(current_time, self.last_turn) > 5:

            self.last_turn = current_time

            # Ignore rotation while button is pressed
            if self.button.value() == 1:

                if self.b.value():
                    self.fifo.put(-1)
                else:
                    self.fifo.put(1)

    def button_handler(self, pin):

        current_time = ticks_ms()

        # Button pressed
        if pin.value() == 0 and not self.button_locked:

            # Check debounce time
            if ticks_diff(current_time, self.last_press) > 50:

                self.last_press = current_time
                self.button_locked = True

                # Send button event to FIFO
                self.fifo.put(2)

        # Button released
        elif pin.value() == 1:

            self.button_locked = False


# FIFO setup

events = Fifo(30, typecode="i")


# Hardware setup

rot = Encoder(10, 11, 12, events)


# LEDs

leds = [Pin(22, Pin.OUT), Pin(21, Pin.OUT), Pin(20, Pin.OUT)]

# Start with all LEDs OFF
for led in leds:
    led.value(0)


# LED states

led_states = [False, False, False]


# Currently selected menu item

selected = 0


# OLED setup

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)

oled = SSD1306_I2C(128, 64, i2c)


# Draw OLED menu


def draw_menu():

    oled.fill(0)

    for i in range(3):

        y = 16 + i * 16

        # Show arrow next to selected LED
        if i == selected:
            arrow = "->"
        else:
            arrow = "  "

        # Display LED name
        oled.text(arrow + "Led " + str(i + 1), 5, y)

        # Display LED state
        if led_states[i]:
            state = "ON"
        else:
            state = "OFF"

        oled.text(state, 85, y)

    oled.show()


draw_menu()

while True:

    # Process all events in FIFO
    while events.has_data():

        event = events.get()

        # Encoder turned clockwise
        if event == 1:

            selected = (selected + 1) % 3

        # Encoder turned counterclockwise
        elif event == -1:

            selected = (selected - 1) % 3

        # Encoder button pressed
        elif event == 2:

            # Toggle selected LED state
            led_states[selected] = not led_states[selected]

            # Update physical LED
            leds[selected].value(led_states[selected])

        # Update OLED after processing event
        draw_menu()

    sleep_ms(5)
