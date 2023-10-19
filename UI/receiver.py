"""
This module handles commands received from the server for mouse and keyboard control.

This module contains the Receiver class, which establishes a connection with the server,
receives commands, and performs appropriate actions based on the received commands.
It handles mouse movements, clicks, keyboard input, and screen sharing commands.

"""

# isort: off
import socket
import time
import pyautogui
import options

# Global variables to track mouse and keyboard state


class Receiver:
    """
    Receiver class handles commands received from the server for mouse and keyboard control.
    """

    def __init__(self, ip_address, port, screen_share):
        """
        Initializes the Receiver object.

        Args:
            ip_address (str): IP address to bind the receiver to.
            port (int): Port number to listen for incoming connections.
            screen_share (bool): Bool indicating whether screen sharing is enabled.
        """
        self.ip_address = ip_address
        self.port = port
        self.send_screen = False
        self.currently_pressed_keys = []

        # Create a socket object and check validity
        return_value = self.create_server()
        if not return_value or self.client_socket is None:
            return

        pyautogui.FAILSAFE = False

        # Set the socket to non-blocking mode
        self.client_socket.setblocking(True)

        # Handle the connection
        while options.RUNNING:
            try:
                data = b""

                # Receive data until a newlin character (\r\n) is received
                # or the chunk is empty
                while (b"\r\n" not in data) and options.RUNNING:
                    if not options.RUNNING:
                        break

                    # Recive data chunks of 1024 bytes and append to data
                    chunk = self.client_socket.recv(1024)
                    data += chunk

                    # If the received chunk is empty, the client has disconnected
                    if not chunk:
                        options.ERROR = True
                        options.RUNNING = False
                        options.ERROR_MESSAGE = "Connection Clossed by Sender"
                        data = False
                        break

                # If no data is received, the client has disconnected and break to loop
                if not data:
                    break

                # Decode the bytes and split data into packets
                data_s = data.decode().split("\r\n", 1)[0]

                # Split the packets into individual commands
                packet = data_s.split("\x03")

                # Print out the received packet
                print("Received:")
                print(packet)
                print("\n")

                # Determine the type of command and call the appropriate handler
                # M = Mouse Movement
                # S = Mouse Scroll
                # C = Mouse Click
                # K = Keyboard
                # I = Screen Share
                try:
                    return_value = True
                    if packet[0] == "M":
                        return_value = self.handle_mouse(packet)
                    elif packet[0] == "S":
                        return_value = self.handle_scroll(packet)
                    elif packet[0] == "C":
                        return_value = self.handle_click(packet)
                    elif packet[0] == "K":
                        return_value = self.handle_keyboard(packet)
                    # elif packet[0] == "I":
                    #     print("Received I")
                    #     screen_share_state = bool(str(packet[1]))
                    #     if screen_share_state and screen_share:
                    #         self.send_screen = True
                    #     print(screen_share_state)

                    # If the return value is False, the client has disconnected
                    if return_value is False:
                        print("Client disconnected or error occurred")
                        break

                # Handle malformed packets
                except IndexError:
                    print("Malformed packet received")

            # Handle socket errors
            except socket.error as e:
                print("Socket error while receiving data: ", e)
                options.ERROR = True
                options.RUNNING = False
                options.ERROR_MESSAGE = "Socket error while receiving data: " + str(e)
                self.client_socket.close()
                self.socket_fd.close()
                return

        # Close the connections
        self.client_socket.close()
        self.socket_fd.close()

        return

    def handle_click(self, packet):
        """
        Handles a mouse click command received from the server.

        Args:
            packet (list): A list of strings containing the command data.
            The list should have the following format: [button, x_coordinate, y_coordinate]

        Returns:
            None
        """
        try:
            # Extract the button and coordinates from the packet
            clicked_button = str(packet[1])
            x_coordinate = int(packet[2])
            y_coordinate = int(packet[3])

            # Print a message indicating the button and coordinates
            print(
                "Clicked: "
                + str(clicked_button)
                + " X: "
                + str(x_coordinate)
                + " Y: "
                + str(y_coordinate)
            )

            # Perform the appropriate mouse action based on the received button
            # l = left click
            # r = right click
            # m = middle click
            # u = mouse release
            if clicked_button == "l":
                pyautogui.mouseDown(button="left", _pause=False)
            elif clicked_button == "r":
                pyautogui.mouseDown(button="right", _pause=False)
            elif clicked_button == "m":
                pyautogui.mouseDown(button="middle", _pause=False)
            elif clicked_button == "u":
                pyautogui.mouseUp(_pause=False)

        # Handle malformed packets
        except IndexError:
            print("Malformed packet received")
            return False
        return True

    def handle_scroll(self, packet):
        """
        Handles a mouse scroll command received from the server.

        Args:
            packet (list): A list of strings containing the command data.
            The list should have the following format: [scroll_direction]

        Returns:
            None
        """
        try:
            # Extract the scroll direction from the packet
            scroll_direction = str(packet[1])

            # Print a message indicating the scroll direction
            print("Scrolling " + scroll_direction)

            # Scroll the mouse up or down based on the received direction
            if scroll_direction == "d":
                pyautogui.scroll(clicks=-1, _pause=False)
            elif scroll_direction == "u":
                pyautogui.scroll(clicks=1, _pause=False)
        except IndexError:
            # Handle malformed packets by printing an error message and returning
            print("Malformed packet received")
            return False
        return True

    def handle_mouse(self, packet):
        """
        Handles a mouse movement command received from the server.

        Args:
            packet (list): A list of strings containing the command data.
            The list should have the following format:
            [screen_width, screen_height, x_coordinate, y_coordinate]

        Returns:
            None
        """
        try:
            receiver_screen_width, receiver_screen_height = pyautogui.size()

            # receive data from the server
            try:
                screen_width = int(packet[1])
                screen_height = int(packet[2])
                x_coordinate = int(packet[3])
                y_coordinate = int(packet[4])

                normalized_x = x_coordinate * (receiver_screen_width / screen_width)
                normalized_y = y_coordinate * (receiver_screen_height / screen_height)

                # Move mouse to received position
                pyautogui.moveTo(normalized_x, normalized_y, _pause=False)

            except IndexError:
                print("Malformed packet received")
                return False
        except KeyboardInterrupt:
            # close the connection
            print("Keyboard Interrupt")
            return False
        return True

    def handle_keyboard(self, packet):
        """
        Handles a keyboard packet received from the server.

        Args:
            packet (str): The packet received from the server.

        Returns:
            None
        """
        try:
            # Extract the key state and key pressed from the packet
            key_state = str(packet[1])
            key_pressed = str(packet[2])

            # Print the key state and key pressed for debugging purposes
            print("Key State: " + key_state)
            print("Key Pressed: " + key_pressed)

            # Check for special characters like ctrl + c, ctrl + v, ctrl + t, ctrl + z

            # Check if the key is being pressed or released
            # P = Press
            # R = Release
            if key_state == "P":
                pyautogui.keyDown(key_pressed, _pause=False)
                self.currently_pressed_keys.append(key_pressed)
            elif key_state == "R":
                pyautogui.keyUp(key_pressed, _pause=False)
                if key_pressed in self.currently_pressed_keys:
                    self.currently_pressed_keys.remove(key_pressed)

        # Handle malformed packets
        except IndexError:
            print("Malformed packet received")
            return False
        return True

    def create_server(self):
        """
        Creates a server socket to listen for incoming connections.

        Returns:
            bool: True if the server socket is successfully created, False otherwise.
        """
        # Create a socket object
        accepted_connection = False
        self.socket_fd = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.client_socket = None
        try:
            # Bind the socket to a specific address and port
            self.socket_fd.bind((self.ip_address, int(self.port)))

            # Listen for incoming connections
            self.socket_fd.listen(1)

            # Accept a single incoming connection
            self.socket_fd.settimeout(0.1)
            print("Waiting for connection")
            while accepted_connection is False:
                try:
                    # Accept the connection
                    self.client_socket, self.client_address = self.socket_fd.accept()

                    # If the connection is accepted, send a 1 comfirmation to the server
                    if self.client_socket:
                        accepted_connection = True
                        # self.client_socket.sendall(b"1")
                # Handle socket timeout
                except socket.timeout:
                    if not options.RUNNING:
                        return False

        # Handle socket errors
        except socket.error:
            options.ERROR = True
            options.RUNNING = False
            options.ERROR_MESSAGE = (
                "Unable to bind to IP Address "
                + str(self.ip_address)
                + " and port "
                + str(self.port)
            )

            # Print an error message and return False
            print("Unable to bind to port " + str(self.port))
            return False

        return True

    def close_connection(self):
        """
        Closes the connection and releases pressed keys and mouse buttons.
        """
        # Release all pressed keys
        for key in self.currently_pressed_keys:
            pyautogui.keyUp(key, _pause=False)

        # Release mouse button, if any is pressed
        pyautogui.mouseUp(_pause=False)

        # Close the client socket if it is a valid socket object
        if self.client_socket and isinstance(self.client_socket, socket.socket):
            self.client_socket.close()

        # Close the server socket
        self.socket_fd.close()


def create_receiver_connection(stop_threading_event, receiver_options):
    """
    Function to create a receiver object and handle incoming connections.

    Args:
        stop_threading_event (threading.Event): Event to signal when the thread should stop.
        receiver_options (dict): Dictionary containing receiver configuration options.

    Returns:
        bool: False when the connection is closed.
    """

    # Create a receiver object
    receiver = Receiver(
        receiver_options["ip_address"],
        receiver_options["port"],
        receiver_options["screen_share"],
    )
    while not stop_threading_event.is_set():
        # Do some work
        time.sleep(0.1)
    print("Closing connection")
    receiver.close_connection()
    return False
