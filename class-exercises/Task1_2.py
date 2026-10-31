from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

max_lines = 8

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

oled.fill(0)
oled.show()

line = 0

while True:
    text= input("Enter a text: ")
    
    if line < max_lines:
        y= line* 8
        line= line+ 1
        
    else:
        oled.scroll(0, -8)
        y= oled.height - 8
        oled.fill_rect(0, 56, 128, 8, 0)
        
    oled.text(text, 0, y)
    oled.show()
        
        
        
        