## Project Task 2.3
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time
from filefifo import Filefifo

button_sw1 = Pin(9, Pin.IN, Pin.PULL_UP)

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

oled.fill(0)
oled.text("Task 2.3 - press SW1", 0, 28, 1)
oled.show()

while button_sw1.value() == 1:
    time.sleep(0.05)

sample_rate = 250
two_sec_samples = int(2 * sample_rate)

fifo = Filefifo(10, name='sinewave_250Hz_03.txt')

initial_window = []
for _ in range(two_sec_samples):
    if fifo.has_data():
        initial_window.append(fifo.get())

min_val = min(initial_window)
max_val = max(initial_window)
threshold = ((min_val + max_val) / 2.0)

rising_edges = []
below = True
sample_index = two_sec_samples

while True:
    if fifo.has_data():
        val = fifo.get()
        
        if below and val >= threshold:
            rising_edges.append(sample_index)
            below = False
        elif not below and val < threshold:
            below = True
            
        sample_index += 1
        
        if len(rising_edges) >= 5:
            intervals = [rising_edges[i+1] - rising_edges[i] for i in range(len(rising_edges) - 1)]
            period = (sum(intervals) / len(intervals)) / sample_rate
            freq = 1.0 / period
            
            oled.fill(0)
            oled.text(f"Freq: {freq:.2f} Hz", 0, 28, 1)
            oled.show()
            print(f"Detected Frequency: {freq:.2f} Hz")
            
            rising_edges.pop(0)
