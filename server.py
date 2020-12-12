from bottle import route, run, get, post, response, static_file, request
import os
import RPi.GPIO as GPIO
import threading
import time

GPIO.setmode (GPIO.BOARD)

@route ("/")
def do_root_index ():
    print ("do_root_index (\"/\") is invoked ==> ./index.html will be executed ...")
    return static_file ("index.html", root = ".")

@route ("/gpio", method = "POST")
def read_gpio ():
    gpio_msg = os.popen ("gpio readall")
    return gpio_msg.read ()

@route ("/gpio_write", method = "POST")
def write_pin ():
    pin = int (request.forms.get ("pin"))
    state = int (request.forms.get ("state").strip ())

    if (state == 1):
        GPIO.output (pin, GPIO.LOW)
    else:
        GPIO.output (pin, GPIO.HIGH)

@route ("/gpio_mode", method = "POST")
def set_mode_pin ():
    pin = int (request.forms.get ("pin"))
    mode = request.forms.get ("mode").strip ()

    if (mode == "IN"):
        GPIO.setup (pin, GPIO.OUT)
    else:
        GPIO.setup (pin, GPIO.IN)

@route ("/gpio_pwm_cdc", method = "POST")
def pwm_cdc ():
    pin = request.forms.get ("pin")
    if (pin == ""):
        return "<script style=\"text/javascript\">alert (\"Bad num of pin\");</script>"
    else:
        pin = int (pin)

    if (pwm_list[pin][4] == False):
        return "<script style=\"text/javascript\">alert (\"You need to set pwm data first\");</script>"

    pwm = int (request.forms.get ("pwm"))
    pwm_list[pin][1] = pwm

# pwm_pin, pwm_value, pwm_start, pwm_end
pwm_list = [[None, 0, 0, 0, True] for i in range (41)]
@route ("/gpio_pwm", method = "POST")
def pwm_pin ():
    pwm_pin = request.forms.get ("gpio_pin")

    if (pwm_pin == ""):
        return "<script style=\"text/javascript\">alert (\"Bad num of pin\"); history.back ();</script>"
    else:
        pwm_pin = int (pwm_pin)
        if (pwm_pin < 1 or pwm_pin > 40):
            return "<script style=\"text/javascript\">alert (\"Bad num of pin\"); history.back ();</script>"
    
    pwm_value = request.forms.get ("pwm_value")

    if (pwm_value == ""):
        return "<script style=\"text/javascript\">alert (\"Input num of pwm value\"); history.back ();</script>"
    else:
        pwm_value = int (pwm_value)

    pwm_start = request.forms.get ("pwm_range_start")

    if (pwm_start == ""):
        return "<script style=\"text/javascript\">alert (\"Input num of pwm start \"); history.back ();</script>"
    else:
        pwm_start = int (pwm_start)

    pwm_end = request.forms.get ("pwm_range_end")

    if (pwm_end == ""):
        return "<script style=\"text/javascript\">alert (\"Input num of pwm end \"); history.back ();</script>"
    else:
        pwm_end = int (pwm_end)
        if (pwm_end > 100):
           return "<script style=\"text/javascript\">alert (\"Bad num of pwm end (0 ~ 100)\"); history.back ();</script>"
            

    if (pwm_list[pwm_pin][0] != None):
        pwm_list[pwm_pin][4] = False

    pwm_list[pwm_pin][0] = threading.Thread (target = pwm_thread, daemon = True, args = [pwm_pin])
    pwm_list[pwm_pin][1] = pwm_value
    pwm_list[pwm_pin][2] = pwm_start
    pwm_list[pwm_pin][3] = pwm_end
    pwm_list[pwm_pin][4] = True
    pwm_list[pwm_pin][0].start ()

    return "<script style=\"text/javascript\">history.back ()</script>"

@route ("/gpio_pwm_reset", method = "POST")
def pwm_reset ():
    pwm_pin = request.forms.get ("gpio_pin")

    if (pwm_pin == ""):
        return "<script style=\"text/javascript\">alert (\"Bad num of pin\"); history.back ();</script>"
    else:
        pwm_pin = int (pwm_pin)
        if (pwm_pin < 1 or pwm_pin > 40):
            return "<script style=\"text/javascript\">alert (\"Bad num of pin\"); history.back ();</script>"

    pwm_list[pwm_pin][4] = False

    return "<script style=\"text/javascript\">history.back ()</script>"

def pwm_thread (pin):
    GPIO.setup (pin, GPIO.OUT)
    pwm = GPIO.PWM (pin, pwm_list[pin][3])
    pwm.start (pwm_list[pin][2])
    while pwm_list[pin][4]:
        pwm.ChangeDutyCycle (pwm_list[pin][1])
        time.sleep (0.1)

not_available = [1, 2, 4, 6, 9, 14, 17, 20, 25, 27, 28, 30, 34, 39]
def check_pin_available (pin):
    for i in not_available:
        if pin == i:
            return False
    return True

@route ("/gpio40")
def gpio40_index ():
    for  i in range (1, 41):
        if (check_pin_available (i) == True):
            GPIO.setup (i, GPIO.OUT)
            GPIO.output (i, GPIO.LOW)
    print ("gpio40_index (\"/\") is invoked ==> ./gpio40x.html will be executed ...")
    return static_file ("gpio40.html", root = ".")

@route ("/gpio40_output", method = "POST")
def gpio40_output ():
    gpio_pin = int (request.forms.get ("pin"))
    gpio_mode = int (request.forms.get ("mode"))

    GPIO.setup (gpio_pin, GPIO.OUT)
    GPIO.output (gpio_pin, gpio_mode)

@route ("/gpio40_pwm_ready", method = "POST")
def gpio40_pwm_ready ():
    pwm_pin = int (request.forms.get ("pin"))

    if (pwm_list[pwm_pin][0] != None):
        pwm_list[pwm_pin][4] = False

    pwm_list[pwm_pin][0] = threading.Thread (target = pwm_thread, daemon = True, args = [pwm_pin])
    pwm_list[pwm_pin][1] = 0
    pwm_list[pwm_pin][2] = 0
    pwm_list[pwm_pin][3] = 100
    pwm_list[pwm_pin][4] = True
    pwm_list[pwm_pin][0].start ()

@route ("/gpio40_pwm_cdc", method = "POST")
def gpio40_pwm_cdc ():
    pwm_pin = int (request.forms.get ("pin"))
    pwm_value = int (request.forms.get ("pwm"))

    pwm_list[pwm_pin][1] = pwm_value

@route ("/gpio40_pwm_stop", method = "POST")
def gpio40_pwm_stop ():
    pwm_pin = int (request.forms.get ("pin"))
    pwm_list[pwm_pin][4] = False

run (host = "165.229.185.179", port = 80, server = "paste")
#run (host = "192.168.0.1", port = 80, server = "paste")
