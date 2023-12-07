"""
This module performs UI automation tests.
"""
# isort: off
import time
import pyautogui
import pytest

from main import App
from main import validate_ip_address, validate_port_number

from receiver import Receiver
from receiver import handle_mouse

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


def test_ip_address_field():
    """
    Tests to see if the Ip address field stores the correct value.
    """
    app = App()
    try:

        def test():
            # Process all idle tasks to ensure the widget is drawn on the screen
            app.update_idletasks()

            # Get the position of the receiver_radio_button
            x = app.ip_address_entry.winfo_rootx()
            y = app.ip_address_entry.winfo_rooty()

            # Move the mouse to the position + padding of the receiver_radio_button
            pyautogui.moveTo((x + 8), (y + 8), _pause=False)

            # Wait until the button is visible or enabled
            while not app.ip_address_entry.winfo_viewable():
                time.sleep(0.1)

            # Perform the click
            pyautogui.click()
            # Clear the Ip address field
            app.ip_address_entry.delete(0, "end")
            pyautogui.write("192.168.1.90")

            # Schedule the assertion check to run after a delay
            app.after(100, check_service_choice)

        def check_service_choice():
            # Get the value of service_choice
            service_choice = app.ip_address_entry.get()
            assert service_choice == "192.168.1.90"

            app.stop_threading_event.set()
            app.destroy()  # Close the window and stop the Tkinter event loop

        # Schedule the test function to run after the tkinter main loop has started
        app.after(100, test)

        app.mainloop()
    except RuntimeError:
        print("RuntimeError")


def test_port_field():
    """
    Tests to see if the Port field stores the correct value.
    """
    app = App()
    try:

        def test():
            # Process all idle tasks to ensure the widget is drawn on the screen
            app.update_idletasks()

            # Get the position of the receiver_radio_button
            x = app.port_entry.winfo_rootx()
            y = app.port_entry.winfo_rooty()

            # Move the mouse to the position + padding of the receiver_radio_button
            pyautogui.moveTo((x + 8), (y + 8), _pause=False)

            # Wait until the button is visible or enabled
            while not app.port_entry.winfo_viewable():
                time.sleep(0.1)

            # Perform the click
            pyautogui.click()
            # Clear the Port field
            app.port_entry.delete(0, "end")
            pyautogui.write("5000")

            # Schedule the assertion check to run after a delay
            app.after(100, check_service_choice)

        def check_service_choice():
            # Get the value of service_choice
            service_choice = app.port_entry.get()
            assert service_choice == "5000"

            app.stop_threading_event.set()
            app.destroy()  # Close the window and stop the Tkinter event loop

        # Schedule the test function to run after the tkinter main loop has started
        app.after(100, test)

        app.mainloop()
    except RuntimeError:
        print("RuntimeError")


def test_ip_address_placeholder_change():
    """
    Tests to see if after clicking the receiver_radio_button the Ip address field has the correct placeholder.
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
            service_choice = app.get_ip_placeholder()
            assert service_choice == "Device IP Address"

            app.stop_threading_event.set()
            app.destroy()  # Close the window and stop the Tkinter event loop

        # Schedule the test function to run after the tkinter main loop has started
        app.after(100, test)

        app.mainloop()
    except RuntimeError:
        print("RuntimeError")


def test_port_placeholder_change():
    """
    Tests to see if after clicking the receiver_radio_button the Port field has the correct placeholder.
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
            service_choice = app.get_port_placeholder()
            assert service_choice == "Port Number"

            app.stop_threading_event.set()
            app.destroy()  # Close the window and stop the Tkinter event loop

        # Schedule the test function to run after the tkinter main loop has started
        app.after(100, test)

        app.mainloop()
    except RuntimeError:
        print("RuntimeError")


def test_validate_ip_address():
    """
    Tests to see if the validate_ip_address function returns the correct value.
    """
    assert validate_ip_address("192.168.1.1") is True
    assert validate_ip_address("10.0.0.1") is True
    assert validate_ip_address("255.255.255.255") is True

    assert validate_ip_address("256.256.256.256") is False
    assert validate_ip_address("192.168.0.256") is False
    assert validate_ip_address("192.168.1") is False


def test_validate_port_number():
    """
    Tests to see if the validate_port_number function returns the correct value.
    """
    assert validate_port_number(5000) is True
    assert validate_port_number(2) is True
    assert validate_port_number(65535) is True

    assert validate_port_number(0) is False
    assert validate_port_number(65536) is False
    assert validate_port_number("test") is False
    assert validate_port_number(65535.0) is False
    assert validate_port_number(-1) is False

def test_mouse_movement():
    """
    Tests to see if the mouse moves when the mouse packet is received.
    """
    packet = ["S", pyautogui.size().width, pyautogui.size().height, 10, 10]
    handle_mouse(packet)
    assert pyautogui.position() == (10, 10)

def test_keyboard_press():
    """
    Tests to see if the keyboard presses when the keyboard packet is received.
    """
    packet = ["K", "P", "a"]
    Receiver.currently_pressed_keys = []
    Receiver.handle_keyboard(Receiver, packet)
    assert Receiver.currently_pressed_keys[0] == "a"  # Check if the 'a' key is pressed
    pyautogui.keyUp("a")  # Release the 'a' key

def test_apperance_mode_light_button():
    """
    Tests to see if after clicking the apperance_mode_button and selecting light mode,
    the apperance_mode_button has the correct text and the UI changes color.
    """
    app = App()
    try:

        def test():
            # Process all idle tasks to ensure the widget is drawn on the screen
            app.update_idletasks()

            # Get the position of the receiver_radio_button
            x = app.appearance_mode_option_menu.winfo_rootx()
            y = app.appearance_mode_option_menu.winfo_rooty()

            # Move the mouse to the position + padding of the receiver_radio_button
            pyautogui.moveTo((x + 8), (y + 8), _pause=False)

            # Wait until the button is visible or enabled
            while not app.appearance_mode_option_menu.winfo_viewable():
                time.sleep(0.1)

            # Perform the click
            pyautogui.click()

            # Schedule the assertion check to run after a delay
            app.after(100, choose_light_option)

        def choose_light_option():
            # Get the value of service_choice
            pyautogui.moveRel(40, 40)
            pyautogui.click()
            app.after(100, check_service_choice)

        def check_service_choice():
            # Get the value of service_choice
            service_choice = app.appearance_mode_option_menu.get()
            assert service_choice == "Light"
            assert app.get_apperance_mode_color() == "light"
            app.stop_threading_event.set()
            app.destroy()  # Close the window and stop the Tkinter event loop

        # Schedule the test function to run after the tkinter main loop has started
        app.after(100, test)

        app.mainloop()
    except RuntimeError:
        print("RuntimeError")


def test_apperance_mode_system_button():
    """
    Tests to see if after clicking the apperance_mode_button and selecting system mode,
    the apperance_mode_button has the correct text and the UI changes color.
    """
    app = App()
    try:

        def test():
            # Process all idle tasks to ensure the widget is drawn on the screen
            app.update_idletasks()

            # Get the position of the receiver_radio_button
            x = app.appearance_mode_option_menu.winfo_rootx()
            y = app.appearance_mode_option_menu.winfo_rooty()

            # Move the mouse to the position + padding of the receiver_radio_button
            pyautogui.moveTo((x + 8), (y + 8), _pause=False)

            # Wait until the button is visible or enabled
            while not app.appearance_mode_option_menu.winfo_viewable():
                time.sleep(0.1)

            # Perform the click
            pyautogui.click()

            # Schedule the assertion check to run after a delay
            app.after(100, choose_light_option)

        def choose_light_option():
            # Get the value of service_choice
            pyautogui.moveRel(40, 65)
            pyautogui.click()
            app.after(100, check_service_choice)

        def check_service_choice():
            # Get the value of service_choice
            service_choice = app.appearance_mode_option_menu.get()
            assert service_choice == "Dark"
            assert app.get_apperance_mode_color() == "dark"
            app.stop_threading_event.set()
            app.destroy()  # Close the window and stop the Tkinter event loop

        # Schedule the test function to run after the tkinter main loop has started
        app.after(100, test)

        app.mainloop()
    except RuntimeError:
        print("RuntimeError")


def test_status_messages():
    """
    Tests to see if the status message changes when the user clicks start button
    """
    app = App()
    try:

        def test():
            # Ensure the status message is not empty
            assert app.program_status.get() != ""
            # Process all idle tasks to ensure the widget is drawn on the screen
            app.update_idletasks()

            # Get the position of the receiver_radio_button
            x = app.start_service_button.winfo_rootx()
            y = app.start_service_button.winfo_rooty()

            # Move the mouse to the position + padding of the receiver_radio_button
            pyautogui.moveTo((x + 8), (y + 8), _pause=False)

            # Wait until the button is visible or enabled
            while not app.start_service_button.winfo_viewable():
                time.sleep(0.1)

            # Clear the ip address and port fields
            app.ip_address_entry.delete(0, "end")
            app.port_entry.delete(0, "end")
            # Perform the click
            pyautogui.click()

            # Schedule the assertion check to run after a delay
            app.after(100, check_service_choice)

        def check_service_choice():
            # Asset that the status message displays an error message
            assert app.program_status.get() == "Error: Invalid IP Address or Port"
            app.stop_threading_event.set()
            app.destroy()  # Close the window and stop the Tkinter event loop

        # Schedule the test function to run after the tkinter main loop has started
        app.after(100, test)

        app.mainloop()
    except RuntimeError:
        print("RuntimeError")


# def test_start_button():
#     """
#     Tests to see if the start button disables the stop button
#     """
#     app = App()
#     try:

#         def test():
#             # Process all idle tasks to ensure the widget is drawn on the screen
#             app.update_idletasks()
#             # Get the position of the receiver_radio_button
#             x = app.receiver_radio_button.winfo_rootx()
#             y = app.receiver_radio_button.winfo_rooty()

#             # Move the mouse to the position + padding of the receiver_radio_button
#             pyautogui.moveTo((x + 8), (y + 8), _pause=False)

#             # Wait until the button is visible or enabled
#             while not app.receiver_radio_button.winfo_viewable():
#                 time.sleep(0.1)

#             # Perform the click
#             pyautogui.click()

#             # Schedule the assertion check to run after a delay
#             app.after(100, click_start_button)

#         def click_start_button():
#             # Process all idle tasks to ensure the widget is drawn on the screen
#             app.update_idletasks()

#             # Get the position of the receiver_radio_button
#             x = app.start_service_button.winfo_rootx()
#             y = app.start_service_button.winfo_rooty()

#             # Move the mouse to the position + padding of the receiver_radio_button
#             pyautogui.moveTo((x + 8), (y + 8), _pause=False)

#             # Wait until the button is visible or enabled
#             while not app.start_service_button.winfo_viewable():
#                 time.sleep(0.1)

#             # Clear the ip address and port fields
#             app.ip_address_entry.delete(0, "end")
#             app.port_entry.delete(0, "end")

#             app.ip_address_entry.insert(0, "127.0.0.1")
#             app.port_entry.insert(0, "5000")
#             pyautogui.click()

#             # Schedule the assertion check to run after a delay
#             app.after(100, check_service_choice)

#         def check_service_choice():
#             # Asset that the status message displays an error message
#             assert app.get_start_button_state() == "disabled"
#             assert app.get_stop_button_state() == "normal"
#             app.stop_threading_event.set()
#             app.destroy()  # Close the window and stop the Tkinter event loop

#         # Schedule the test function to run after the tkinter main loop has started
#         app.after(100, test)

#         app.mainloop()
#     except RuntimeError:
#         print("RuntimeError")


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
