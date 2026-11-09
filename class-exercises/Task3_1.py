from machine import Pin, PWM
import time

led_pwm = PWM(Pin(20)) # Convert the LED connected to pin GP20 into PWM mode.
led_pwm.freq(1000)     # PWM signal's frequency 1000Hz              

# Setup encoder inputs (a/b for rotation, sw for button) with pull-ups
rot_a = Pin(10, Pin.IN, Pin.PULL_UP)   
rot_b = Pin(11, Pin.IN, Pin.PULL_UP)  
rot_sw = Pin(12, Pin.IN, Pin.PULL_UP) 

fifo = []        # FIFO buffer to store encoder rotation directions from ISR
led_on = False   # Track LED ON/OFF state (starts OFF)
brightness = 50  # Initial LED brightness level (50%)

# Interrupt Service Routine(ISR) to detect turn direction without controlling the LED directly
def encoder_isr(pin):
    global fifo            # To use fifo inside this function
    if rot_b.value() == 0: # Check b, not a
        fifo.append(1)     # Clockwise turn  
    else:
        fifo.append(-1)    # Counter-clockwise turn
        
# Attach an interrupt to rot_a on falling edge to trigger the ISR automatically
rot_a.irq(trigger=Pin.IRQ_FALLING, handler=encoder_isr)

prev_sw_val = 1          # Store previous button state to detect new presses (1 = released)
last_debounce_time = 0   # Timestamp of the last valid button press for debouncing

print("Task 3.1 Started. Push the Encoder.")

while True:
    sw_val = rot_sw.value() # Read current hardware state of the encoder button
    current_time = time.ticks_ms() # Get current timestamp in milliseconds for debounce check
    
    # Filter button press (detect new falling edge with 200ms debounce interval)
    if sw_val == 0 and prev_sw_val == 1 and (current_time - last_debounce_time) > 200:
        led_on = not led_on  # Toggle LED state (ON to OFF, or OFF to ON)
        last_debounce_time = current_time  # Update last valid press timestamp
        print(f"LED State: {'ON' if led_on else 'OFF'}")
    prev_sw_val = sw_val     # Save current switch state for edge detection in next iteration
    
    # Process encoder rotation events stored in FIFO buffer
    if len(fifo) > 0:
        direction = fifo.pop(0)  # Retrieve and remove the oldest turn direction (1 or -1)
        if led_on:
            brightness += direction * 5  # Adjust brightness by +/- 5%
            brightness = max(0, min(100, brightness)) # Clamp brightness between 0% and 100%
            print(f"Brightness: {brightness}%")

    # Update physical LED brightness using PWM duty cycle
    if led_on:
        duty_cycle = int((brightness / 100.0) * 65535) # Scale percentage (0-100) to 16-bit PWM (0-65535)
        led_pwm.duty_u16(duty_cycle) # Apply brightness to LED
    else:
        led_pwm.duty_u16(0)          # Turn off LED completely (0% duty cycle)

    time.sleep(0.01)                 