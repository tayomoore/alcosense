import RPi.GPIO as GPIO
from picamera import PiCamera
from PIL import Image
import numpy as np
import time
import random
 
# Setup GPIO pins
RIGHT = 11
SELECT = 13
LEFT = 15
KILL = 16
 
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(RIGHT, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(SELECT, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LEFT, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(KILL, GPIO.IN)
 
camera = PiCamera()
 
def press_button(pin):
    """General function to simulate pressing a button."""
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.1)  # Debounce delay
 
def capture_image():
    """Captures an image and returns it as a numpy array."""
    camera.resolution = (320, 240)  # Set a lower resolution, e.g., 320x240
    camera.capture('current_view.jpg')
    img = Image.open('current_view.jpg')
    return np.array(img)
 
def calculate_red_and_blue(image_array):
    """Calculates the average red value of an image."""
    red_channel = image_array[:, :, 0]  # Extract the red channel
    blue_channel = image_array[:, :, 2]  # Extract the red channel
    average_red = np.mean(red_channel)
    average_blue = np.mean(blue_channel)
    return average_red, average_blue
 
def is_guess_incorrect():
    """Determines if the password guess is incorrect by analyzing the captured image."""
    image_array = capture_image()
    red, blue = calculate_red_and_blue(image_array)
    print("Red: " + str(red))
    print("Blue: " + str(blue))
    if 130 <= red <= 190 and 70 <= blue <= 110:
        print("looks like a red cross")
        return True
    else:
        print("doesn't look like a red cross")
        return False
 
def enter_digit(digit_value):
    """Enters a single hexadecimal digit."""
    # Convert digit to integer if its a hexadecimal character
    if isinstance(digit_value, str):
        digit_value = int(digit_value, 16)
    for _ in range(digit_value):
        press_button(RIGHT)
    press_button(SELECT)
    time.sleep(0.1)  # Small delay after selecting
 
def try_password(password):
    """Tries entering a given password."""
    for digit in password:
        enter_digit(digit)
 
def load_tried_passwords():
    """Loads previously tried passwords from a file."""
    try:
        with open('tried_passwords.txt', 'r') as file:
            return [line.strip() for line in file]
    except FileNotFoundError:
        return []
 
def main():
    manual_buttons()
    user_input = input("enter admin mode?")
    if user_input == "y":
        enter_admin_mode()
 
    user_input = input("good to start attempting?")
    if user_input == "y":
        tried_passwords = load_tried_passwords()
        try:
            with open('tried_passwords.txt', 'a') as file:
                hex_passwords = [format(i, "04x").upper() for i in range(0x0000, 0x10000)]
                print("Before removal of tried passwords: " + str(len(hex_passwords)))
                hex_passwords = [hp for hp in hex_passwords if hp not in tried_passwords]  # Exclude tried passwords
                print("After removal of tried passwords: " + str(len(hex_passwords)))
                random.shuffle(hex_passwords)
                for hex_pass in hex_passwords:
                    should_it_stop()
                    digit_list = list(hex_pass)
                    print(f"Trying password: {hex_pass}")
                    file.write(f"{hex_pass}\n")
                    try_password(digit_list)
                    time.sleep(0.1)  # Wait for the red cross to appear, if present
                    if is_guess_incorrect():
                        print("Incorrect password, trying next...")
                    else:
                        print("Password found:", hex_pass)
                        break
                    press_button(SELECT)  # Reset for next attempt
                    time.sleep(0.1)
        finally:
            GPIO.cleanup()  # Clean up GPIO to ensure a clean exit
    else:
        GPIO.cleanup()
 
def should_it_stop():
    pin_state = GPIO.input(KILL)
    if pin_state == GPIO.HIGH:
        GPIO.cleanup()
        exit()
    else:
        return
 
def enter_admin_mode():
    GPIO.output(SELECT, GPIO.HIGH)
    time.sleep(2)  # Simulate button press duration
    GPIO.output(SELECT, GPIO.LOW)
    time.sleep(0.1)  # Debounce delay
    GPIO.output(LEFT, GPIO.HIGH)
    GPIO.output(RIGHT, GPIO.HIGH)
    time.sleep(5)
    GPIO.output(LEFT, GPIO.LOW)
    GPIO.output(RIGHT, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(SELECT, GPIO.HIGH)
    time.sleep(0.1)  # Simulate button press duration
    GPIO.output(SELECT, GPIO.LOW)
    GPIO.output(LEFT, GPIO.HIGH)
    GPIO.output(RIGHT, GPIO.HIGH)
    time.sleep(1.5)
    GPIO.output(LEFT, GPIO.LOW)
    GPIO.output(RIGHT, GPIO.LOW)
    return
 
def manual_buttons():
    while True:
        key = input("What to send")
        if key == "l":
            print("pressing left")
            press_button(LEFT)
        elif key == "r":
            print("pressing right")
            press_button(RIGHT)
        elif key == "s":
            print("pressing select")
            press_button(SELECT)
        elif key == "p":
            GPIO.output(SELECT, GPIO.HIGH)
            time.sleep(3)  # Simulate button press duration
            GPIO.output(SELECT, GPIO.LOW)
        elif key == "q":
            return
 
 
if __name__ == "__main__":
    main()
