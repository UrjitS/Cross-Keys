"""
This module performs UI automation tests.
"""
import time
import pyautogui
import pytest

from main import App


def test_options_sender_update_state():
    """
    Tests clicking the sender_radio_button and checks the value of service_choice.
    """
    app = App()
    try:

        def test():
            # Process all idle tasks to ensure the widget is drawn on the screen
            app.update_idletasks()

            # Get the position of the sender_radio_button
            x = app.sender_radio_button.winfo_rootx()
            y = app.sender_radio_button.winfo_rooty()

            # Move the mouse to the position + padding of the sender_radio_button
            pyautogui.moveTo((x + 8), (y + 8), _pause=False)

            # Wait until the button is visible or enabled
            while not app.sender_radio_button.winfo_viewable():
                time.sleep(0.1)

            # Perform the click
            pyautogui.click()

            # Schedule the assertion check to run after a delay
            app.after(100, check_service_choice)

        def check_service_choice():
            # Get the value of service_choice
            service_choice = app.radio_button_value.get()
            assert service_choice == 0

            app.stop_threading_event.set()
            app.destroy()  # Close the window and stop the Tkinter event loop

        # Schedule the test function to run after the tkinter main loop has started
        app.after(100, test)

        app.mainloop()

    except RuntimeError:
        print("RuntimeError")


def test_options_receiver_update_state():
    """
    Tests clicking the receiver_radio_button and checks the value of service_choice.
    """
    app = App()
    try:

        def test():
            # Process all idle tasks to ensure the widget is drawn on the screen
            app.update_idletasks()

            # Get the position of the receiver_radio_button
            x = app.receiver_radio_button.winfo_rootx()
            y = app.receiver_radio_button.winfo_rooty()

            # Move the mouse to the position + padding of the receiver_radio_button
            pyautogui.moveTo((x + 8), (y + 8), _pause=False)

            # Wait until the button is visible or enabled
            while not app.receiver_radio_button.winfo_viewable():
                time.sleep(0.1)

            # Perform the click
            pyautogui.click()

            # Schedule the assertion check to run after a delay
            app.after(100, check_service_choice)

        def check_service_choice():
            # Get the value of service_choice
            service_choice = app.radio_button_value.get()
            assert service_choice == 1

            app.stop_threading_event.set()
            app.destroy()  # Close the window and stop the Tkinter event loop

        # Schedule the test function to run after the tkinter main loop has started
        app.after(100, test)

        app.mainloop()
    except RuntimeError:
        print("RuntimeError")


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
