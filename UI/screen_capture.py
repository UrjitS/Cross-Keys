"""
This module is used to capture the screen of the user's computer.
"""
from mss import mss

with mss() as sct:
    screenshot = sct.shot()

# def capture_screen():
#     """
#     This function is used to capture the screen of the user's computer.
#     """

#     screenshot = pyautogui.screenshot()
#     screenshot.show()

# def main():
#     """
#     This is the main function of the module.
#     """
#     capture_screen()

# if __name__ == "__main__":
#     main()
    