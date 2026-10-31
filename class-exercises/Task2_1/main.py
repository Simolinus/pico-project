from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from filefifo import Filefifo



class PositivePeaks:
    def __init__(self, data_list):
        self.data_list = data_list

    def peak(self):
        pos_peaks = []
        for i in range(1, len(self.data_list) - 1):
            if self.data_list[i] >= self.data_list[i-1] and self.data_list[i] > self.data_list[i+1]:
                pos_peaks.append(i)
                
        return pos_peaks

    def interval(self):
        pos_peaks = self.peak()
        intervals = []

        for i in range(1, len(pos_peaks)):
            interval = pos_peaks[i] - pos_peaks[i-1]
            intervals.append(interval)

        return intervals

def get_data():
    fifo = Filefifo(10, name = "sinewave_250Hz_01.txt")
    data_list = []

    for _ in range(1000):
        if fifo.has_data():
            data = fifo.get()
            data_list.append(data)

    return data_list

def main():
    i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
    oled = SSD1306_I2C(128, 64, i2c)

    data_list = get_data()
    peaks = PositivePeaks(data_list)

    intervals = peaks.interval()

    ts = 1000 / 250
    total = 0
    line = 0
    max_lines = 8

    oled.fill(0)

    for interval in intervals:
        ppi = interval * ts
        total += interval

        if line < max_lines:
            y = line * 8
            line += 1
        else:
            oled.scroll(0, -8)
            y = 56
            oled.fill_rect(0, 56, 128, 8, 0)

        oled.text(f"{line}){interval}-{int(ppi)}ms", 0, y)
        oled.show()

    if len(intervals) > 0:
        average_interval = total / len(intervals)
        frequency = 250 / average_interval

        if line < max_lines:
            y = line * 8
        else:
            oled.scroll(0, -8)
            y = 56
            oled.fill_rect(0, 56, 128, 8, 0)

        oled.text(f"freq {frequency:.3f}Hz", 0, y)
        oled.show()


if __name__ == "__main__":
    main()
