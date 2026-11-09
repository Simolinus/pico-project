from machine import Pin, I2C
from fifo import Fifo
from filefifo import Filefifo
from ssd1306 import SSD1306_I2C
import micropython


class Encoder:
    def __init__(self, rot_a, rot_b):
        self.a = Pin(rot_a, mode=Pin.IN)
        self.b = Pin(rot_b, mode=Pin.IN)
        self.fifo = Fifo(30, typecode="i")
        self.a.irq(handler=self.handler, trigger=Pin.IRQ_RISING, hard=True)

    def handler(self, pin):
        if self.b():
            self.fifo.put(-1)  # anticlockwise
        else:
            self.fifo.put(1)  # clockwise


# Initial I2C Screen
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

# Create 10 buff in Fifo to read 1000 row from the text file
filefifo = Filefifo(10, name="week3_data.txt")
data = []
for i in range(1000):
    data.append(filefifo.get())

# Calculate the minimum and maximum data
low = min(data)
high = max(data)


# Scale the data between 0 and 63
def scale(num):
    diff = high - low
    if diff == 0:
        diff = 1
    return int(63 - (num - low) / diff * 63)


rot = Encoder(10, 11)
position = 0
MAX_POSITION = len(data) - 128  # last data


# Draw the 128 points based on the current data
def draw_screen():
    oled.fill(0)
    for x in range(128):
        if position + x < len(data):
            y = scale(data[position + x])
            oled.pixel(x, y, 1)
    oled.show()


draw_screen()

while True:
    updated = False

    while rot.fifo.has_data():
        current = rot.fifo.get()
        position += current

        # Set the limitation
        if position < 0:
            position = 0
        elif position > MAX_POSITION:
            position = MAX_POSITION

        updated = True

    if updated:
        draw_screen()
