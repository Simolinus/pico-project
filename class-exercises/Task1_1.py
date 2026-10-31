from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf

button_0 =  Pin(9, Pin.IN, Pin.PULL_UP)
button_2 =  Pin(7, Pin.IN, Pin.PULL_UP)

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
text_width = 8*3
oled = SSD1306_I2C(128, 64, i2c)
x = 0
y= oled.height - 8

while True:
    if button_0() == 0:
        if(x < oled.width - text_width):
            oled.fill(0)
            oled.text('<=>', x, y, 1)
            oled.show()        
            x += 1
            
    if button_2() == 0:
        if(x > 0):
            oled.fill(0)
            oled.text('<=>', x, y, 1)
            oled.show()        
            x -= 1        


