from machine import Pin, I2C
from ssd1306 import SSD1306_I2C


class draw:
    def __init__(self, oled, start_pos):
        self.oled = oled
        self.start_pos = start_pos
        self.x = self.start_pos["x"]
        self.y = self.start_pos["y"]

    def move_down(self):
        if self.y < self.oled.height - 1:
            self.y += 1

    def move_up(self):
        if self.y > 0:
            self.y -= 1

    def draw_oled(self):
        self.oled.pixel(self.x, self.y, 1)

        self.x += 1

        if self.x >= self.oled.width:
            self.x = self.start_pos["x"]

    def clear(self):
        self.oled.fill(0)
        self.x = self.start_pos["x"]
        self.y = self.start_pos["y"]
        self.oled.show()


def main():
    button_sw0 = Pin(9, Pin.IN, Pin.PULL_UP)
    button_sw1 = Pin(8, Pin.IN, Pin.PULL_UP)
    button_sw2 = Pin(7, Pin.IN, Pin.PULL_UP)

    i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
    oled = SSD1306_I2C(128, 64, i2c)

    start_pos = {"x": 0, "y": oled.height // 2}
    line = draw(oled, start_pos)

    line.clear()

    while True:
        if button_sw0.value() == 0:
            line.move_down()

        if button_sw1.value() == 0:
            line.clear()

        if button_sw2.value() == 0:
            line.move_up()

        line.draw_oled()
        if line.x % 8 == 0:
            oled.show()


if __name__ == "__main__":
    main()
