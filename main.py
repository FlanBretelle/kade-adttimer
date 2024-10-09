from machine import Pin, I2C
from utime import sleep, sleep_ms, ticks_ms, ticks_diff
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

buttonGPIONum = 18
myButton = Pin(buttonGPIONum, Pin.IN, Pin.PULL_UP)

buttonLEDGPIONum = 13
myButtonLED = Pin(buttonLEDGPIONum, Pin.OUT)
myButtonLED.value(1)

# Define I2C parameters (adjust if using a different I2C bus)
I2C_ADDR = 0x27  # I2C address of the 16x2 LCD with I2C backpack
I2C_SDA = 0      # SDA pin number (GP0)
I2C_SCL = 1      # SCL pin number (GP1)

# Initialize I2C
i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400000)
try:
    lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)  # Create an LCD instance
except:
    while True:
        myButtonLED.toggle()
        sleep(0.1)
lcd.display_off()
lcd.backlight_off()



state = 0
button_pressed = False
run_start_time = 0
press_start_time = 0
press_duration = 0


def startupAnimation(lcd, base_message = "EEM OPSTARTEN", cycles = 3):
    for i in range(cycles):
        for dots in range(4):
            lcd.clear()
            lcd.putstr(base_message)
            lcd.putstr("." * dots)
            sleep(0.3)
            
def typingAnimation(lcd, txt_line_one, txt_line_two = None, cursor_visible = True, typing_speed = 0.2):
    if cursor_visible:
        lcd.show_cursor()
        lcd.blink_cursor_on()
    else:
        lcd.hide_cursor()
        lcd.blink_cursor_off()
    
    lcd.move_to(0, 0)
    for character in txt_line_one:
        lcd.putchar(character)
        sleep(typing_speed)
    
    if txt_line_two:
        lcd.move_to(0, 1)
        for character in txt_line_two:
            lcd.putchar(character)
            sleep(typing_speed)
        
def backspaceAnimation(lcd, txt, cursor_visible = True, typing_speed = 0.2):
    if cursor_visible:
        lcd.show_cursor()
        lcd.blink_cursor_on()
    else:
        lcd.hide_cursor()
        lcd.blink_cursor_off()
    
    
    col = len(txt) -1
    row = 0
    
    for i in range(len(txt)):
        lcd.move_to(col, row)
        lcd.putchar(" ")
        lcd.move_to(col, row)
        sleep(typing_speed)
        col -= 1




while True:
    
    
    if state == 0: #machine off
        button_pressed = False
        
        if myButton.value() == 0:
            lcd.display_on()
            lcd.backlight_on()
            startupAnimation(lcd, cycles = 3)
            lcd.clear()
            sleep(0.75)
            typingAnimation(lcd, "WELKOM!")
            sleep(1.75)
            backspaceAnimation(lcd, "WELKOM!")
            sleep(1)
            typingAnimation(lcd, txt_line_one = "DRUK OP DE KNOP", txt_line_two = "OM TE STARTEN!", typing_speed = 0.15)
            main_menu_start_time = ticks_ms()
            state = 1
            
    elif state == 1: #main menu
        if myButton.value() == 0 and not button_pressed:
            run_start_time = ticks_ms()
            lcd.hide_cursor()
            lcd.clear()
            lcd.putstr("RENNEN!!!")
            myButtonLED.value(1)
            state = 2
        else:
            main_menu_elapsed_time = ticks_diff(ticks_ms(), main_menu_start_time)
            milliseconds = (main_menu_elapsed_time % 1000) // 10
            
            if milliseconds < 50:
                myButtonLED.value(0)
            else:
                myButtonLED.value(1)
                
    elif state == 2: #running
        elapsed_time = ticks_diff(ticks_ms(), run_start_time)
        
        # Convert elapsed time to minutes, seconds, and milliseconds
        minutes = elapsed_time // 60000
        seconds = (elapsed_time // 1000) % 60
        milliseconds = (elapsed_time % 1000) // 10
        
        # Display time in mm:ss:ms format
        lcd.move_to(0, 1)  # Move to the second line
        lcd.putstr("{:02}:{:02}:{:02}".format(minutes, seconds, milliseconds))

        # Brief pause for screen update
        sleep_ms(20)
        
        
        if myButton.value() == 0 and not button_pressed:
            press_start_time = ticks_ms()
            button_pressed = True
            
        elif myButton.value() == 0 and button_pressed:
            press_duration = ticks_diff(ticks_ms(), press_start_time)
            
            if press_duration > 1500:
                state = 4
        
        elif myButton.value() == 1 and button_pressed:
            
            
            elapsed_time = ticks_diff(ticks_ms(), run_start_time)
            
            # Convert elapsed time to minutes, seconds, and milliseconds
            minutes = elapsed_time // 60000
            seconds = (elapsed_time // 1000) % 60
            milliseconds = (elapsed_time % 1000) // 10
            
            if not (seconds == 0 and milliseconds < 99):
                button_pressed = False
                lcd.clear()
                lcd.putstr("FINISH!")
            
                # Display time in mm:ss:ms format
                lcd.move_to(0, 1)  # Move to the second line
                lcd.putstr("{:02}:{:02}:{:02}".format(minutes, seconds, milliseconds))
                sleep(2)
                state = 3
    
            
    elif state == 3: #finished
        if myButton.value() == 0 and not button_pressed:
            press_start_time = ticks_ms()
            button_pressed = True
            
        elif myButton.value() == 0 and button_pressed:
            press_duration = ticks_diff(ticks_ms(), press_start_time)
            
            if press_duration > 1500:
                state = 4
                
        elif myButton.value() == 1 and button_pressed:
            lcd.clear()
            typingAnimation(lcd, txt_line_one = "DRUK OP DE KNOP", txt_line_two = "OM TE STARTEN!", typing_speed = 0.15)
            main_menu_start_time = ticks_ms()
            button_pressed = False
            state = 1
        
        
    elif state == 4: #turning off
        lcd.clear()
        lcd.putstr("DE GROETEN HE!")
        sleep(2)
        lcd.backlight_off()
        lcd.clear()
        lcd.display_off()
        state = 0
        sleep(3)
        
    sleep(.1)
    