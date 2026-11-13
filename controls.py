
import pyautogui

# Safety setting
pyautogui.FAILSAFE = True

def volume_up():
    pyautogui.press("volumeup")
    print("Volume increased!")

def volume_down():
    pyautogui.press("volumedown")
    print("Volume decreased!")

def play_pause():
    pyautogui.press("space")
    print("Media play/pause!")

def scroll_up():
    pyautogui.scroll(3)
    print("Scrolling up!")

def next_slide():
    pyautogui.press("right")
    print("Next slide!")

def previous_slide():
    pyautogui.press("left")
    print("Previous slide!")

print("AirCommand controls loaded!")
