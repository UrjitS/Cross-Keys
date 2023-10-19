# isort: False
import socket
import time
import pyautogui
import options
from pynput import keyboard
from pynput import mouse


KeyMap = {
    "alt_l": "altleft",
    "alt_r": "altright",
    "ctrl_l": "ctrlleft",
    "ctrl_r": "ctrlright",
    "media_volume_up": "volumeup",
    "media_volume_down": "volumedown",
    "media_volume_mute": "volumemute",
    "page_up": "pgup",
    "media_play_pause": "playpause",
}

class Sender:
    global CLIENT_ADDRESS
    CLIENT_ADDRESS = None

    def __init__(self, ip_address, port, screen_share=False):
        self.TRACK_MOUSE = True
        self.TRACK_KEYBOARD = True
        self.CLIENT_ADDRESS = None
        self.socket_fd = None
        pyautogui.FAILSAFE = False
        self.currently_pressed_keys = list()
        self.keyboard_thread = None
        self.mouse_thread = None
        self.current_mouse_position = pyautogui.position()

        # Create a TCP socket object
        self.socket_fd = self.create_client_connection(ip_address, port, screen_share)

        if not self.socket_fd or not isinstance(self.socket_fd, socket.socket):
            options.ERROR = True
            options.RUNNING = False
            options.ERROR_MESSAGE = (
                "Unable to connect to IP Address "
                + str(ip_address)
                + " and port "
                + str(port)
            )
            return

        print("Connected to IP Address " + str(ip_address) + " and port " + str(port))
        # Start key logging
        def on_press(event):
            self.on_press(event)
        def on_release(event):
            self.on_release(event)
        self.keyboard_thread = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.keyboard_thread.start()

        # Start mouse logging
        self.mouse_thread = mouse.Listener(
            on_click=lambda x, y, button, pressed: self.on_click(
                x=x, y=y, button=button, pressed=pressed
            ),
            on_scroll=lambda x, y, dx, dy: self.on_scroll(x=x, y=y, dx=dx, dy=dy),
            on_move=lambda x, y: self.send_mouse_position(x=x, y=y),
        )
        self.mouse_thread.start()

        print("Mouse thread started")
        return

    def send_to_client(self, message):
        print("Sending message to client: " + message.decode())
        if (not options.RUNNING) or (not isinstance(self.socket_fd, socket.socket)):
            print("Not running")
            return False
        try:
            # Send the message to the server
            self.socket_fd.sendall(message)
        except ConnectionAbortedError:
            options.ERROR = True
            options.RUNNING = False
            options.ERROR_MESSAGE = "Connection Clossed by Receiver"
            return False
        return True

    # KEYBOARD HANDLERS
    #               WINDOWS                                                     LINUX
    # If key == '//x03' then ctrl + c     or    if self.currently_pressed_keys.count(ctrl) and key == 'c' then ctrl + c
    def on_press(self, key):
        """
        Purpose:
            key press event handler.
        Args:
            key (pynput.keyboard.Key): The key that was pressed.
        Returns:
            bool: True if the event was handled successfully, False otherwise.
        """
        # Check if the program is running and if a socket is available
        if (not options.RUNNING) or (not isinstance(self.socket_fd, socket.socket)):
            print("Not running")
            return False

        # Construct the packet header
        packet_header = f"K{chr(3)}"

        try:
            # Check if the key is an alphanumeric key
            key_pressed = key.char

            # Check if keyboard and mouse tracking are enabled
            if not self.TRACK_KEYBOARD or not self.TRACK_MOUSE:
                return

            # Check if the key is currently pressed
            if self.currently_pressed_keys.count(key_pressed) == 0:
                # Add the key to the list of currently pressed keys
                self.currently_pressed_keys.append(key_pressed)

                # Construct the packet body
                packet_body = f"P{chr(3)}{str(key_pressed)}{chr(3)}\r\n"

                # Send the packet to the server
                self.send_to_client(bytes((packet_header + packet_body), "utf-8"))

                # Print a message indicating that the packet was sent
                print("Sent " + packet_header + packet_body)
        except BrokenPipeError:
            return False
        except AttributeError:  # Special Characters i.e. tab, alt, space, ctrl
            # Extract the special key that was pressed
            special_key_pressed = str(key)[4:]

            # Handle the case where the print screen key is pressed
            if special_key_pressed == "print_screen":
                print("Hit Hot Key")
                if not self.TRACK_KEYBOARD:
                    options.ENABLE_FULLSCREEN = True
                self.TRACK_KEYBOARD = not self.TRACK_KEYBOARD
                self.TRACK_MOUSE = not self.TRACK_MOUSE

            # Check if keyboard and mouse tracking are enabled
            if not self.TRACK_KEYBOARD or not self.TRACK_MOUSE:
                return

            # Map the special key to a more readable format if possible
            if special_key_pressed in KeyMap:
                special_key_pressed = KeyMap.get(special_key_pressed)

            # Check if the special key is currently pressed
            if self.currently_pressed_keys.count(special_key_pressed) == 0:
                # Add the special key to the list of currently pressed keys
                self.currently_pressed_keys.append(special_key_pressed)

                # Construct the packet body
                packet_body = f"P{chr(3)}{str(special_key_pressed)}{chr(3)}\r\n"

                # Send the packet to the server
                self.send_to_client(bytes((packet_header + packet_body), "utf-8"))

                # Print a message indicating that the packet was sent
                print("Sent " + packet_header + packet_body)

    def on_release(self, key):
        """
        Purpose:
            Key release event handler
        Args:
            key (pynput.keyboard.Key): The key that was released.

        Returns:
            bool: True if the event was handled successfully, False otherwise.
        """
        # Check if the program is running and if a socket is available
        if (not options.RUNNING) or (not isinstance(self.socket_fd, socket.socket)):
            print("Not running")
            return False

        # Construct the packet header
        packet_header = f"K{chr(3)}"

        try:
            # Check if keyboard and mouse tracking are enabled
            if not self.TRACK_KEYBOARD or not self.TRACK_MOUSE:
                return

            # Extract the key that was released
            key_pressed = key.char

            # Check if the key is currently pressed
            if self.currently_pressed_keys.count(key_pressed) > 0:
                # Remove the key from the list of currently pressed keys
                self.currently_pressed_keys.remove(key_pressed)

                # Construct the packet body
                packet_body = f"R{chr(3)}{str(key_pressed)}{chr(3)}\r\n"

                # Send the packet to the server
                self.send_to_client(bytes((packet_header + packet_body), "utf-8"))

                # Print a message indicating that the packet was sent
                print("Sent " + packet_header + packet_body)
        except BrokenPipeError:
            return False
        except AttributeError:  # Special Characters i.e. tab, alt, space, ctrl
            # Check if keyboard and mouse tracking are enabled
            if not self.TRACK_KEYBOARD or not self.TRACK_MOUSE:
                return

            # Extract the special key that was released
            special_key_pressed = str(key)[4:]

            # Map the special key to a more readable format if possible
            if special_key_pressed in KeyMap:
                special_key_pressed = KeyMap.get(special_key_pressed)

            # Check if the special key is currently pressed
            if self.currently_pressed_keys.count(special_key_pressed) > 0:
                # Remove the special key from the list of currently pressed keys
                self.currently_pressed_keys.remove(special_key_pressed)

                # Construct the packet body
                packet_body = f"R{chr(3)}{str(special_key_pressed)}{chr(3)}\r\n"

                # Send the packet to the server
                self.send_to_client(bytes((packet_header + packet_body), "utf-8"))

                # Print a message indicating that the packet was sent
                print("Sent " + packet_header + packet_body)

    # MOUSE STUFF
    def send_mouse_position(self, x, y):
        """
        Purpose:
            Sends a mouse movement packet to the remote server over the network.
        Args:
            x (int): The x-coordinate of the mouse cursor.
            y (int): The y-coordinate of the mouse cursor.
        Returns:
            bool: True if the packet was sent successfully, False otherwise.
        """
        # Packet Body = Key_Identifier ETX Screen_Width ETX Screen_Height ETX X_COORD ETX Y_COORD ETX CRLF
        if (not options.RUNNING) or (not isinstance(self.socket_fd, socket.socket)):
            print("Not running")
            return False
        if (
            (not self.TRACK_KEYBOARD)
            or (not self.TRACK_MOUSE)
            or (self.current_mouse_position == (x, y))
        ):
            return

        print("Mouse moved to ({0}, {1})".format(x, y))

        # Get the size of the primary screen and convert the coordinates to strings
        print("Sending")
        x_coord_bytes = str(x)
        y_coord_bytes = str(y)

        screenWidth, screenHeight = pyautogui.size()
        screenWidth = str(screenWidth)
        screenHeight = str(screenHeight)

        # Create the packet header and body
        packet_header = f"M{chr(3)}"
        packet_body = f"{screenWidth}{chr(3)}{screenHeight}{chr(3)}{x_coord_bytes}{chr(3)}{y_coord_bytes}{chr(3)}\r\n"

        self.send_to_client(bytes((packet_header + packet_body), "utf-8"))
        self.current_mouse_position = (x, y)
        print("Sent " + packet_header + packet_body)

    def on_click(self, x, y, button, pressed):
        """
        Purpose:
            Sends a mouse click command to the server over the network.

        Args:
            x (int): The x-coordinate of the mouse cursor.
            y (int): The y-coordinate of the mouse cursor.
            button (str): The button that was clicked ("Button.left", "Button.right", or "Button.middle").
            pressed (bool): True if the button was pressed, False if it was released.

        Returns:
            bool: True if the command was sent successfully, False otherwise.
        """
        if (not options.RUNNING) or (not isinstance(self.socket_fd, socket.socket)):
            print("Not running")
            return False
        if not self.TRACK_KEYBOARD or not self.TRACK_MOUSE:
            return

        clicked_button = str(button)[7:][:1]
        packet_header = f"C{chr(3)}"

        clicked_button = clicked_button if clicked_button in ["l", "r"] else "m"

        if pressed:
            packet_body = (
                f"{clicked_button}{chr(3)}{str(x)}{chr(3)}{str(y)}{chr(3)}\r\n"
            )
            self.send_to_client(bytes((packet_header + packet_body), "utf-8"))
            print("Sent " + packet_header + packet_body)
        else:
            packet_body = f"u{chr(3)}{str(x)}{chr(3)}{str(y)}{chr(3)}\r\n"
            self.send_to_client(bytes((packet_header + packet_body), "utf-8"))

            print("Sent " + packet_header + packet_body)

    def on_scroll(self, x, y, dx, dy):
        """
        Purpose:
            Sends a scroll command to the server over the network.

        Args:
            x (int): The x-coordinate of the mouse cursor.
            y (int): The y-coordinate of the mouse cursor.
            dx (int): The horizontal distance scrolled.
            dy (int): The vertical distance scrolled.

        Returns:
            bool: True if the command was sent successfully, False otherwise.
        """
        if (not options.RUNNING) or (not isinstance(self.socket_fd, socket.socket)):
            print("Not running")
            return False
        if not self.TRACK_KEYBOARD or not self.TRACK_MOUSE:
            return
        # Key_Identifier ETX Scroll_Direction ETX CRLF
        scroll_direction = "d" if dy < 0 else "u"
        packet = f"S{chr(3)}{scroll_direction}{chr(3)}\r\n"
        self.send_to_client(bytes(packet, "utf-8"))

    def create_client_connection(self, ip_address, port, sender_options):
        """
        Purpose:
            Creates a TCP connection to the server.

        Args:
            ip_address (str): The IP address of the server.
            port (int): The port number of the server.
            sender_options (dict): The options that the sender has selected.

        Return:
            client_socket (socket.socket): The socket object that was created.
        """
        # Create a TCP socket object
        CLIENT_ADDRESS = (ip_address, port)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(1)  # Set a timeout value of 5 seconds

        try:
            # Connect to the server
            client_socket.connect(CLIENT_ADDRESS)

            # Convert the boolean to a string and encode as a byte string
            screen_share_packet = (
                f"I{chr(3)}" + str(sender_options) + f"{chr(3)}" + "\r\n"
            )

            # Send the message to the server
            client_socket.sendall(bytes(screen_share_packet, "utf-8"))

            # Read the response from the server

        except (socket.error, ConnectionRefusedError, OSError) as e:
            print("Socket error:", e)
            options.ERROR = True
            options.RUNNING = False
            options.ERROR_MESSAGE = "Error connecting to the server: " + str(e)
            return None

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(1)  # Set a timeout value of 5 seconds

        try:
            # Connect to the server
            client_socket.connect(CLIENT_ADDRESS)

            # Convert the boolean to a string and encode as a byte string
            screen_share_packet = (
                f"I{chr(3)}" + str(sender_options) + f"{chr(3)}" + "\r\n"
            )

            # Send the message to the server
            client_socket.sendall(bytes(screen_share_packet, "utf-8"))

            # Read the response from the server

        except (socket.error, ConnectionRefusedError, OSError) as e:
            print("Socket error:", e)
            options.ERROR = True
            options.RUNNING = False
            options.ERROR_MESSAGE = "Error connecting to the server: " + str(e)
            return None

        return client_socket

    def close_sender_connection(self):
        """
        Purpose:
            Close connection to sender and stops the keyboard and mouse threads
        Args:
            None
        Return:
            False
        """
        print("Closing connection")
        if isinstance(self.keyboard_thread, keyboard.Listener):
            self.keyboard_thread.stop()
            pyautogui.press("esc")
            self.keyboard_thread.join()

        if isinstance(self.mouse_thread, mouse.Listener):
            self.mouse_thread.stop()
            pyautogui.moveTo(pyautogui.position())
            self.mouse_thread.join()

        if isinstance(self.socket_fd, socket.socket):
            self.socket_fd.close()
        pyautogui.press("esc")
        return False


def create_sender_connection(stop_threading_event, sender_options):
    """
    Purpose:
        Creates a TCP connection to the server.

    Args:
        stop_threading_event (threading.Event): The event that will be used to stop the thread.
        sender_options (dict): The options that the sender has selected.

    Return:
        False

    """
    receiver = Sender(
        sender_options["ip_address"],
        sender_options["port"],
        sender_options["screen_share"],
    )

    while not stop_threading_event.is_set():
        # Do some work
        time.sleep(0.1)

    print("Closing connection")
    receiver.close_sender_connection()
    return False
