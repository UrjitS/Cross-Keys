"""
This module contains the main application for the Cross Keyboard program.
"""
# isort: off
import json
import threading
import tkinter as tk
import tkinter.messagebox
import ipaddress
import re

import customtkinter

import options
from receiver import create_receiver_connection
from sender import create_sender_connection

customtkinter.set_appearance_mode(
    "System"
)  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme(
    "green"
)  # Themes: "blue" (standard), "green", "dark-blue"


def change_appearance_mode_event(new_appearance_mode: str):
    """
    Changes the appearance mode of the application.

    Parameters:
    new_appearance_mode (str): The new appearance mode selected by the user.

    Returns:
    None
    """
    customtkinter.set_appearance_mode(new_appearance_mode)


def change_scaling_event(new_scaling: str):
    """
    Changes the scaling of the widgets in the application.

    Parameters:
    new_scaling (str): The new scaling percentage selected by the user.

    Returns:
    None
    """
    new_scaling_float = int(new_scaling.replace("%", "")) / 100
    customtkinter.set_widget_scaling(new_scaling_float)


def validate_ip_address(ip_address: str):
    """
    Validates the IP address entered by the user.

    Parameters:
    self: The current instance of the App class.

    Returns:
    bool: True if the IP address is valid, False otherwise.
    """
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False


def validate_port_number(port_number: str):
    """
    Validates the port number entered by the user.

    Parameters:
    self: The current instance of the App class.

    Returns:
    bool: True if the port number is valid, False otherwise.
    """
    try:
        # Run the regex to check if the port number is valid
        port_regex = r"^\d{1,5}$"
        port_number = str(port_number)
        regex_status = bool(re.match(port_regex, port_number))
        # Convert the port number to an integer
        port_number_int = int(port_number)
        bound_check_status = 0 < port_number_int <= 65535
        return regex_status and bound_check_status
    except ValueError:
        return False


class App(customtkinter.CTk):  # pylint: disable=R0902
    """
    The main application for the Cross Keyboard program.
    """

    def __init__(self):
        """
        Initializes the Cross Keyboard application.

        Parameters:
        self: The current instance of the App class.

        Returns:
        None
        """
        super().__init__()
        self.stop_threading_event = threading.Event()
        self.receiver_thread = None
        self.sender_thread = None
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.program_status = tk.StringVar()
        self.program_status.set("")
        self.counter = 0
        # configure window
        self.title("Cross Keyboard")
        self.geometry(f"{1920}x{1080}+0+0")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(2, weight=1)

        # Create the three main frames
        self.create_left_sidebar()
        self.create_main_frame()
        self.create_right_sidebar()

        # Set the default values
        self.appearance_mode_option_menu.set("Dark")
        self.scaling_option_menu.set("100%")
        self.program_status.set("Waiting")

        self.after(500, self.update_time)
        # self.after(500, self.display_screen_share)

    def create_left_sidebar(self):
        """
        Creates the left sidebar frame with widgets.

        Parameters:
        self: The current instance of the App class.

        Returns:
        None
        """
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame,
            text="Cross Keyboard",
            font=customtkinter.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.start_service_button = customtkinter.CTkButton(
            self.sidebar_frame, text="Start", command=self.start_service
        )
        self.start_service_button.grid(row=1, column=0, padx=20, pady=10)
        self.stop_service_button = customtkinter.CTkButton(
            self.sidebar_frame, text="Stop", command=self.stop_service, state="disabled"
        )
        self.stop_service_button.grid(row=2, column=0, padx=20, pady=10)

        self.appearance_mode_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Appearance Mode:", anchor="w"
        )
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_option_menu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=change_appearance_mode_event,
        )
        self.appearance_mode_option_menu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="UI Scaling:", anchor="w"
        )
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_option_menu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["80%", "90%", "100%", "110%", "120%"],
            command=change_scaling_event,
        )
        self.scaling_option_menu.grid(row=8, column=0, padx=20, pady=(10, 20))
        self.image_label = customtkinter.CTkLabel(self, text="")

    def create_main_frame(self):
        """
        Creates the main frame of the application.

        Parameters:
        self: The current instance of the App class.

        Returns:
        None
        """
        self.status_output = tk.Label(
            self, textvariable=self.program_status, font=("Arial", 15)
        )

        self.status_output.grid(
            row=3, column=1, columnspan=2, padx=(0, 0), pady=(0, 0), sticky="nsew"
        )

        # create textbox
        self.ip_address_entry = customtkinter.CTkEntry(
            self, width=500, height=50, placeholder_text="Receiver IP Address"
        )
        self.ip_address_entry.grid(row=0, column=1, padx=0, pady=80)
        self.port_entry = customtkinter.CTkEntry(
            self, width=500, height=50, placeholder_text="Receiver Port Number"
        )
        self.port_entry.grid(row=1, column=1, padx=0)

        # Load the data from the file
        try:
            with open("connection.json", "r", encoding="UTF-8") as connection_file:
                data = json.load(connection_file)
        except FileNotFoundError:
            print("File not found: connection.json")
            # Handle the error here
            data = {}
        except json.JSONDecodeError:
            print("Invalid JSON format in connection.json")
            # Handle the error here
            data = {}

        # Extract the IP address and port number
        ip_address = data.get("ip_address", "")
        port_number = data.get("port_number", "")

        if validate_ip_address(ip_address) and validate_port_number(port_number):
            self.ip_address_entry.insert(0, ip_address)
            self.port_entry.insert(0, port_number)

    def create_right_sidebar(self):
        """
        Creates the right sidebar frame with widgets.

        Parameters:
        self: The current instance of the App class.

        Returns:
        None
        """
        # create radiobutton frame
        self.radiobutton_frame = customtkinter.CTkFrame(
            self, width=140, corner_radius=0
        )
        self.radiobutton_frame.grid(
            row=0, column=3, rowspan=4, columnspan=10, sticky="nsew"
        )
        self.radio_button_value = tkinter.IntVar(value=0)
        self.label_radio_group = customtkinter.CTkLabel(
            master=self.radiobutton_frame, text="Options:"
        )
        self.label_radio_group.grid(
            row=0, column=2, columnspan=1, padx=10, pady=10, sticky=""
        )
        self.sender_radio_button = customtkinter.CTkRadioButton(
            master=self.radiobutton_frame,
            border_color="white",
            border_width_unchecked=5,
            border_width_checked=5,
            hover_color="blue",
            command=self.update_text,
            text="Sender   ",
            variable=self.radio_button_value,
            value=0,
        )
        self.sender_radio_button.grid(row=1, column=2, pady=10, padx=20, sticky="n")
        self.receiver_radio_button = customtkinter.CTkRadioButton(
            master=self.radiobutton_frame,
            border_color="white",
            border_width_unchecked=5,
            border_width_checked=5,
            hover_color="blue",
            command=self.update_text,
            text="Receiver",
            variable=self.radio_button_value,
            value=1,
        )
        self.receiver_radio_button.grid(row=2, column=2, pady=10, padx=20, sticky="n")
        self.screen_share_button = customtkinter.CTkCheckBox(
            master=self.radiobutton_frame, text="Screen Share"
        )
        self.screen_share_button.grid(
            row=3, column=2, pady=(20, 0), padx=20, sticky="n"
        )

        self.label_radio_group = customtkinter.CTkLabel(
            master=self.radiobutton_frame,
            text="                          " "         " " \n",
        )
        self.label_radio_group.grid(
            row=6, column=2, columnspan=1, padx=10, pady=900, sticky=""
        )

    def update_text(self):
        """
        Updates the text of the IP address and port number entry fields
        based on the selected radio button.

        Parameters:
        self: The current instance of the App class.

        Returns:
        None
        """
        if self.radio_button_value.get() == 0:
            self.ip_address_entry.configure(placeholder_text="Receiver IP Address")
            self.port_entry.configure(placeholder_text="Receiver Port Number")
        else:
            self.ip_address_entry.configure(placeholder_text="Device IP Address")
            self.port_entry.configure(placeholder_text="Port Number")

    def start_service(self):
        """
        Starts the sender or receiver service based on the selected radio button.

        Parameters:
        self: The current instance of the App class.

        Returns:
        None
        """
        options.RUNNING = True
        options.ERROR = False
        if validate_ip_address(self.ip_address_entry.get()) and validate_port_number(
            self.port_entry.get()
        ):
            self.program_status.set("Starting Service")
            self.stop_threading_event.clear()
            service_choice = self.radio_button_value.get()
            if service_choice == 0:
                # Hide the main frame and the right sidebar frame
                # self.attributes("-fullscreen", True)
                self.port_entry.grid_remove()
                self.ip_address_entry.grid_remove()
                self.radiobutton_frame.grid_remove()  # Hide the right sidebar frame
                self.appearance_mode_label.grid_remove()
                self.appearance_mode_option_menu.grid_remove()
                self.scaling_label.grid_remove()
                self.scaling_option_menu.grid_remove()

                sender_options = {
                    "ip_address": self.ip_address_entry.get(),
                    "port": self.port_entry.get(),
                    "screen_share": self.screen_share_button.get(),
                    "window": None,
                }

                # Start the sender thread
                self.sender_thread = threading.Thread(
                    target=create_sender_connection,
                    args=(self.stop_threading_event, sender_options),
                )
                self.sender_thread.start()
            elif service_choice == 1:
                receiver_options = {
                    "ip_address": self.ip_address_entry.get(),
                    "port": self.port_entry.get(),
                    "screen_share": self.screen_share_button.get(),
                }

                self.receiver_thread = threading.Thread(
                    target=create_receiver_connection,
                    args=(self.stop_threading_event, receiver_options),
                )
                self.receiver_thread.start()
            else:
                self.program_status.set("Error: Invalid IP Address or Port")

            self.program_status.set("Service Running")
            self.start_service_button.configure(state="disabled")  # Disable the button
            self.stop_service_button.configure(state="normal")  # Enable the button
        else:
            self.program_status.set("Error: Invalid IP Address or Port")

    def update_ui_on_stop(self):
        """
        Updates the UI when the service is stopped.

        Parameters:
        self: The current instance of the App class.

        Returns:
        None
        """
        print("Reseting UI")
        self.attributes("-fullscreen", False)  # Exit fullscreen
        self.port_entry.grid()
        self.ip_address_entry.grid()
        self.radiobutton_frame.grid()  # Hide the right sidebar frame
        self.appearance_mode_label.grid()
        self.appearance_mode_option_menu.grid()
        self.scaling_label.grid()
        self.scaling_option_menu.grid()

    def stop_service(self):
        """
        Stops the sender or receiver service and updates the program status label.

        Parameters:
        self: The current instance of the App class.

        Returns:
        None
        """
        options.RUNNING = False
        options.ENABLE_FULLSCREEN = False
        self.stop_threading_event.set()

        if options.ERROR_MESSAGE:
            self.program_status.set("Error: " + options.ERROR_MESSAGE)
        else:
            self.program_status.set("Stopped Service")

        if self.sender_thread is not None and self.sender_thread.is_alive():
            print("Closing Sender")
            self.sender_thread.join()
            self.stop_threading_event.set()
            self.update_ui_on_stop()
        if self.receiver_thread is not None and self.receiver_thread.is_alive():
            print("Closing Receiver")
            self.receiver_thread.join()
            self.stop_threading_event.set()

        self.stop_service_button.configure(state="disabled")  # Disable the stop button
        self.start_service_button.configure(state="normal")  # Enable the start button

    def update_time(self):
        """
        Updates the program status label with the current status of the program.

        Parameters:
        self: The current instance of the App class.

        Returns:
        None
        """
        # change text on Label
        if not options.RUNNING:
            options.UI_RESET = False
            str_message = "Waiting For Start"
            for _ in range(self.counter):
                str_message += "."

            self.program_status.set(str_message)

            if self.counter == 3:
                self.counter = 0
            else:
                self.counter += 1
        if options.ERROR:
            self.program_status.set("Error: " + options.ERROR_MESSAGE)
            options.RUNNING = False
            if not options.UI_RESET:
                self.stop_service()
                options.UI_RESET = True
        if options.ENABLE_FULLSCREEN:
            options.UI_RESET = False
            self.attributes("-fullscreen", True)
            self.focus_set()  # Prevents the window from losing focus
            options.ENABLE_FULLSCREEN = False
        self.after(500, self.update_time)

    def on_closing(self):
        """
        Handles the "WM_DELETE_WINDOW" event.

        Parameters:
        self: The current instance of the App class.

        Returns:
        None
        """
        options.RUNNING = False
        if validate_ip_address(self.ip_address_entry.get()) and validate_port_number(
            self.port_entry.get()
        ):
            ip_address = self.ip_address_entry.get()
            port_number = self.port_entry.get()

            # Save the IP address and port number to a file
            data = {"ip_address": ip_address, "port_number": port_number}
            try:
                with open("connection.json", "w", encoding="UTF-8") as connection_file:
                    json.dump(data, connection_file)
            except FileNotFoundError:
                print("File not found: connection.json")
                # Handle the error here
            except PermissionError:
                print("Permission denied: connection.json")
                # Handle the error here

        self.destroy()

    def get_ip_placeholder(self):
        """
        Returns the placeholder text for the IP address entry field.

        Parameters:
        self: The current instance of the App class.

        Returns:
        str: The placeholder text for the IP address entry field.
        """
        return self.ip_address_entry._placeholder_text  # pylint: disable=W0212

    def get_port_placeholder(self):
        """
        Returns the placeholder text for the port number entry field.

        Parameters:
        self: The current instance of the App class.

        Returns:
        str: The placeholder text for the port number entry field.
        """
        return self.port_entry._placeholder_text  # pylint: disable=W0212

    def get_apperance_mode_color(self):
        """
        Returns the cuurent apperance mode color.

        Parameters:
        self: The current instance of the App class.

        Returns:
        str: The current apperance mode color 'light' or 'dark'.
        """
        return self._get_appearance_mode()  # pylint: disable=W0212

    def get_start_button_state(self):
        """
        Returns the start buttons state.

        Parameters:
        self: The current instance of the App class.

        Returns:
        str: The current state of the start button. disabled or normal.
        """
        return self.start_service_button._state  # pylint: disable=W0212

    def get_stop_button_state(self):
        """
        Returns the stop buttons state.

        Parameters:
        self: The current instance of the App class.

        Returns:
        str: The current state of the stop button. disabled or normal.
        """
        return self.stop_service_button._state  # pylint: disable=W0212


if __name__ == "__main__":
    app = App()
    app.mainloop()
