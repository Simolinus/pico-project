from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from filefifo import Filefifo
import time

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

sw1_pins = [Pin(12, Pin.IN, Pin.PULL_UP), Pin(7, Pin.IN, Pin.PULL_UP), Pin(8, Pin.IN, Pin.PULL_UP), Pin(9, Pin.IN, Pin.PULL_UP)]

oled.fill(0)
oled.text("Task 2.2 - press", 0, 16)
oled.text("SW1", 0, 32)
oled.show()

button_pressed = False
while not button_pressed:
    for btn in sw1_pins:
        if btn.value() == 0:
            button_pressed = True
            break
    time.sleep(0.05)

oled.fill(0)
oled.show()

fifo = Filefifo(10, name="sinewave_250Hz_01.txt")

samples_2s = []
for _ in range(500):
    while not fifo.has_data():
        pass
    samples_2s.append(fifo.get())

min_val = min(samples_2s)
max_val = max(samples_2s)
val_range = max_val - min_val if max_val != min_val else 1

visible_rows = []

for _ in range(2500):
    while not fifo.has_data():
        pass
    raw_val = fifo.get()
    
    scaled_val = int(((raw_val - min_val) / val_range) * 100)
    scaled_val = max(0, min(100, scaled_val))
    
    val_str = f"{scaled_val:3d}"
    line_len = int((scaled_val / 100.0) * 90)
    
    print(f"Scaled value: {val_str}")
    
    visible_rows.append((val_str, line_len))
    if len(visible_rows) > 8:
        visible_rows.pop(0)  
    
    oled.fill(0)
    for row_idx, (text, length) in enumerate(visible_rows):
        y = row_idx * 8
        oled.text(text, 0, y)
        if length > 0:
            oled.hline(30, y + 3, length, 1)
    oled.show()