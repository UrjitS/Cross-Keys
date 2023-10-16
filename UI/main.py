"""
Main file for the Cross Keyboard application.
"""
import json
import re
import tkinter as tk
import tkinter.messagebox

import customtkinter

import options

customtkinter.set_appearance_mode(
    "System"
)  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme(
    "green"
)  # Themes: "blue" (standard), "green", "dark-blue"


def change_appearance_mode_event(new_appearance_mode: str):
    """
    Changes the appearance mode of the application.

    The function is called when the user selects a new appearance mode from the appearance mode option menu. The function
    sets the appearance mode of the application using the `set_appearance_mode` function from the `customtkinter` module.

    Parameters:
    new_appearance_mode (str): The new appearance mode selected by the user.

    Returns:
    None
    """
    customtkinter.set_appearance_mode(new_appearance_mode)


def change_scaling_event(new_scaling: str):
    """
    Changes the scaling of the widgets in the application.

    The function is called when the user selects a new scaling option from the scaling option menu. The function converts
    the scaling percentage to a float and sets the widget scaling using the `set_widget_scaling` function from the
    `customtkinter` module.

    Parameters:
    new_scaling (str): The new scaling percentage selected by the user.

    Returns:
    None
    """
    new_scaling_float = int(new_scaling.replace("%", "")) / 100
    customtkinter.set_widget_scaling(new_scaling_float)


class App(customtkinter.CTk):
    def __init__(self):
        """
        Initializes the Cross Keyboard application.

        The function sets up the main window of the application with a grid layout and creates the left sidebar, main frame, and
        right sidebar frames. The function also sets the default values for the appearance mode and scaling option menus, as
        well as the program status label. The function calls the `update_time` method every 500 milliseconds to update the
        program status label.

        Parameters:
        self (App): The current instance of the App class.

        Returns:
        None
        """
        super().__init__()
        self.receiver_thread = None
        self.sender_thread = None
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.program_status = tk.StringVar()
        self.program_status.set("")
        self.counter = 0
        # configure window
        self.title("Cross Keyboard")
        self.geometry(f"{1920}x{1080}")

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

        # self.after(500, self.update_time)

    def create_left_sidebar(self):
        """
        Creates the left sidebar frame with widgets.

        The left sidebar frame contains the Cross Keyboard logo, start and stop service buttons, and appearance mode and scaling
        option menus. The appearance mode option menu allows the user to select between light, dark, and system appearance modes.
        The scaling option menu allows the user to select between 80%, 90%, 100%, 110%, and 120% UI scaling.

        Parameters:
        self (App): The current instance of the App class.

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

        The main frame contains the IP address and port number entry fields, as well as the program status label. The IP address
        entry field allows the user to enter the IP address of the receiver. The port number entry field allows the user to enter
        the port number of the receiver. The program status label displays the current status of the program, such as "Starting
        Service" or "Service Running".

        Parameters:
        self (App): The current instance of the App class.

        Returns:
        None
        """
        self.status_output = tk.Label(
            self, textvariable=self.program_status, font=("Arial", 15)
        )

        self.status_output.grid(
            row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew"
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
            with open("connection.json", "r") as connection_file:
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

        if self.validate_ip_address(ip_address) and self.validate_port_number(
            port_number
        ):
            self.ip_address_entry.insert(0, ip_address)
            self.port_entry.insert(0, port_number)

    def create_right_sidebar(self):
        """
        Creates the right sidebar frame with widgets.

        The right sidebar frame contains two radio buttons for selecting between sender and receiver modes. The radio buttons
        are contained within a frame with a label that reads "Options:". The radio buttons are styled using the customtkinter
        module to have a white border and blue hover color. The radio buttons are bound to the `update_text` method, which updates
        the program status label with the current mode. The right sidebar frame also contains a label that is used to adjust the
        height of the frame.

        Parameters:
        self (App): The current instance of the App class.

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
        Updates the text of the IP address and port number entry fields based on the selected radio button.

        If the "Sender" radio button is selected, the IP address entry field will display "Receiver IP Address" and the port
        number entry field will display "Receiver Port Number". If the "Receiver" radio button is selected, the IP address entry
        field will display "Device IP Address" and the port number entry field will display "Port Number".

        Parameters:
        self (App): The current instance of the App class.

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

        If the "Sender" radio button is selected, the function creates a new thread to run the `create_sender_connection`
        function with the IP address and port number entered by the user. If the "Receiver" radio button is selected, the
        function creates a new thread to run the `create_receiver_connection` function with the IP address and port number
        entered by the user.

        Parameters:
        self (App): The current instance of the App class.

        Returns:
        None
        """
        options.RUNNING = True
        options.ERROR = False
        if self.validate_ip_address(
            self.ip_address_entry.get()
        ) and self.validate_port_number(self.port_entry.get()):
            self.program_status.set("Starting Sender Service")
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

            elif service_choice == 1:
                print("Receiver")
            else:
                self.program_status.set("Error: Invalid IP Address or Port")

            self.program_status.set("Service Running")
            self.start_service_button.configure(state="disabled")  # Disable the button
            self.stop_service_button.configure(state="normal")  # Enable the button
        else:
            self.program_status.set("Error: Invalid IP Address or Port")

    def validate_ip_address(self, ip_address: str):
        """
        Validates the IP address entered by the user.

        The function retrieves the IP address entered by the user from the IP address entry field and checks if it matches the
        format of a valid IP address. If the IP address is valid, the function returns True. Otherwise, it returns False.

        Parameters:
        self (App): The current instance of the App class.

        Returns:
        bool: True if the IP address is valid, False otherwise.
        """
        ip_address_regex = r"^(\d{1,3}\.){3}\d{1,3}$"
        return bool(re.match(ip_address_regex, ip_address))

    def validate_port_number(self, port_number: str):
        """
        Validates the port number entered by the user.

        The function retrieves the port number entered by the user from the port number entry field and checks if it matches the
        format of a valid port number. If the port number is valid, the function returns True. Otherwise, it returns False.

        Parameters:
        self (App): The current instance of the App class.

        Returns:
        bool: True if the port number is valid, False otherwise.
        """
        port_regex = r"^\d{1,5}$"
        return bool(re.match(port_regex, port_number))

    def update_ui_on_stop(self):
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

        The function sets the `RUNNING` and `ENABLE_FULLSCREEN` variables in the `options` module to False, which stops the
        sender or receiver service. If the sender thread is running, the function calls the `close_sender_connection` function
        to close the connection. The function updates the program status label to "Stopped Service" and disables the stop
        service button while enabling the start service button.

        Parameters:
        self (App): The current instance of the App class.

        Returns:
        None
        """
        options.RUNNING = False
        options.ENABLE_FULLSCREEN = False
        self.program_status.set("Stopped Service")
        self.update_ui_on_stop()

        if self.sender_thread is not None:
            print("Closing Sender")
        if self.receiver_thread is not None:
            print("Closing Receiver")

        self.stop_service_button.configure(state="disabled")  # Disable the stop button
        self.start_service_button.configure(state="normal")  # Enable the start button

    def update_time(self):
        """
        Updates the program status label with the current status of the program.

        The function checks the values of the `RUNNING`, `ERROR`, and `ENABLE_FULLSCREEN` variables in the `options` module
        and updates the program status label accordingly. If `RUNNING` is False, the function displays a "Waiting For Start"
        message with a series of dots to indicate that the program is waiting to start. If `ERROR` is True, the function
        displays an error message. If `ENABLE_FULLSCREEN` is True, the function sets the application to fullscreen mode. The
        function calls itself every 500 milliseconds to update the program status label.

        Parameters:
        self (App): The current instance of the App class.

        Returns:
        None
        """
        # change text on Label
        if not options.RUNNING:
            options.UI_RESET = False
            temp_str = "Waiting For Start"
            for _ in range(self.counter):
                temp_str += "."

            self.program_status.set(temp_str)

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

        The function sets the `RUNNING` variable in the `options` module to False, which stops the sender or receiver service.
        The function then calls the `stop_service` method to stop the service and update the program status label. Finally,
        the function destroys the application window.

        Parameters:
        self (App): The current instance of the App class.

        Returns:
        None
        """
        options.RUNNING = False
        if self.validate_ip_address(
            self.ip_address_entry.get()
        ) and self.validate_port_number(self.port_entry.get()):
            ip_address = self.ip_address_entry.get()
            port_number = self.port_entry.get()

            # Save the IP address and port number to a file
            data = {"ip_address": ip_address, "port_number": port_number}
            try:
                with open("connection.json", "w") as connection_f:
                    json.dump(data, connection_f)
            except FileNotFoundError:
                print("File not found: connection.json")
                # Handle the error here
            except PermissionError:
                print("Permission denied: connection.json")
                # Handle the error here

        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
