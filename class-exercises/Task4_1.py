from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from filefifo import Filefifo

WIDTH, HEIGHT = 128, 64
AVG_N = 5  # samples averaged per pixel
SCALE_N = 250  # samples between scaling/threshold updates
MS_PER_SAMPLE = 4  # 250 Hz
MIN_PPI_MS = 300  # ignore edges closer than this (noise)
THRESHOLD_PERCENT = 70  # threshold position between min and max

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)


# window size for SMA, for example tune between 3 and 8
class SMAFilter:
    def __init__(self, window_size=5):
        self._window_size = window_size
        self._buffer = []

    def update(self, sample):
        # Add the newest sample
        self._buffer.append(sample)

        # Remove oldest sample if window is full
        if len(self._buffer) > self._window_size:
            self._buffer.pop(0)

        # Calculate average using integer division
        return sum(self._buffer) // len(
            self._buffer
        )  # will return the integer smoothed value


sma = SMAFilter()


def threshold(data):
    """Return a threshold THRESHOLD_PERCENT % of the way between min and max."""
    min_val = None
    max_val = None
    for v in data:
        if min_val is None or v < min_val:
            min_val = v
        if max_val is None or v > max_val:
            max_val = v

    return min_val + (max_val - min_val) * THRESHOLD_PERCENT // 100


def scale(value, lo, hi):
    """Map value to 0..63, capped, minimum at the bottom of the screen."""
    if hi == lo:
        return HEIGHT // 2
    y = (value - lo) * (HEIGHT - 1) // (hi - lo)
    y = max(0, min(HEIGHT - 1, y))  # cap: <0 -> 0, >63 -> 63
    return (HEIGHT - 1) - y  # flip: OLED y=0 is the top


def draw(ys):
    """Redraw the trace."""
    oled.fill(0)
    for x in range(1, len(ys)):
        oled.line(x - 1, ys[x - 1], x, ys[x], 1)
    oled.show()


def main():
    filefifo = Filefifo(10, name="hr_capture02_250Hz.txt")

    # First period: collect the initial threshold and scaling range
    data = []  # smoothed samples of the previous period
    first_raw = []
    for _ in range(SCALE_N):
        v = filefifo.get()
        first_raw.append(v)
        data.append(sma.update(v))
    thresh = threshold(data)
    scale_min, scale_max = min(first_raw), max(first_raw)

    new_data = []  # period being collected right now
    cur_min, cur_max = None, None
    block_total, block_count = 0, 0
    ys = []  # y-values on screen (max 128)
    was_above = False
    index = 0
    last_edge = None
    ppi = None

    while True:
        try:
            v = filefifo.get()
        except Exception:
            break  # end of file
        index += 1
        smooth = sma.update(v)

        # Collect data for the next period
        new_data.append(smooth)
        cur_min = v if cur_min is None else min(cur_min, v)
        cur_max = v if cur_max is None else max(cur_max, v)

        # Rising edge detection on the smoothed signal
        is_above = smooth > thresh
        if is_above and not was_above:
            if last_edge is None or (index - last_edge) * MS_PER_SAMPLE >= MIN_PPI_MS:
                if last_edge is not None:
                    ppi = (index - last_edge) * MS_PER_SAMPLE
                last_edge = index
        was_above = is_above

        # Average 5 raw samples -> one pixel
        block_total += v
        block_count += 1
        if block_count == AVG_N:
            ys.append(scale(block_total // AVG_N, scale_min, scale_max))
            if len(ys) > WIDTH:
                ys.pop(0)  # scroll left
            draw(ys)
            block_total, block_count = 0, 0

        # End of period: previous 250 samples become the new range/threshold
        if len(new_data) >= SCALE_N:
            data = new_data
            thresh = threshold(data)
            scale_min, scale_max = cur_min, cur_max
            new_data = []
            cur_min, cur_max = None, None


main()
