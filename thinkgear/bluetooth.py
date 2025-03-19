from typing import Tuple, Optional
import socket  # type: ignore
from thinkgear.think_gear import ThinkGearProtocol

__all__ = ("ThinkGearBluetooth",)


class ThinkGearBluetooth(ThinkGearProtocol):
    """
    A class for managing Bluetooth communication with ThinkGear devices.

    This class extends `ThinkGearProtocol` to implement Bluetooth-specific
    communication protocols. It establishes a Bluetooth connection, facilitates
    data transfer, and manages the connection lifecycle.

    Attributes:
        socket (Optional[socket.socket]): The Bluetooth socket used for communication.
    """

    def __init__(self, debug: bool = False):
        """
        Initialize the ThinkGearBluetooth instance.

        Args:
            debug (bool): Enables debugging mode if True. Defaults to False.
        """
        super().__init__(debug)
        self.socket: Optional[socket.socket] = None

    @staticmethod
    def connect_device(address: Tuple[str, int]) -> Optional[socket.socket]:
        """
        Establish a Bluetooth connection to a ThinkGear device.

        Args:
            address (Tuple[str, int]): A tuple containing the Bluetooth address and port.

        Returns:
            Optional[socket.socket]: The connected socket object, or None if the connection fails.
        """
        soc = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
        )
        soc.connect(address)
        return soc

    def connect(self, address: Tuple[str, int]) -> None:
        """
        Connect to the ThinkGear device using the provided Bluetooth address and port.

        Args:
            address (Tuple[str, int]): A tuple containing the Bluetooth address and port.

        Raises:
            socket.error: If the connection fails.
        """
        self.device = self.connect_device(address)
        if self._debug:
            print(f"Connected to device at {address}.")

    def disconnect(self) -> None:
        """
        Disconnect from the ThinkGear device.

        Closes the Bluetooth socket and sets it to None.
        """
        if self.device is not None:
            self.device.close()
            self.device = None
            if self._debug:
                print("Disconnected from device.")

    def is_connected(self) -> bool:
        """
        Check if the device is currently connected.

        Returns:
            bool: True if the device is connected, False otherwise.
        """
        return self.device is not None

    def get_device(self) -> Optional[socket.socket]:
        """
        Get current instance of bluetooth socket device.

        Returns:
            socket.socket: socket object connected to device
        """
        return self.device

    def _recv(self, size: int = 1) -> bytes:
        """
        Receive data from the ThinkGear device via Bluetooth.

        This method overrides the `_recv` method from `ThinkGearProtocol`.

        Args:
            size (int): The number of bytes to receive. Defaults to 1.

        Returns:
            bytes: The received data. Returns an empty byte string if not connected.
        """
        if self.device is None:
            if self._debug:
                print("Attempt to receive data without an active connection.")
            return b""
        data = self.device.recv(size)
        if self._debug:
            print(f"Received data: {data!r}")
        return data
