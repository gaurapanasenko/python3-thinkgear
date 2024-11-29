from typing import Tuple, Optional, List, Union
import serial  # type: ignore

from thinkgear.think_gear import ThinkGearProtocol

__all__ = ("ThinkGearSerial",)


class ThinkGearSerial(ThinkGearProtocol):
    """
    A class for managing serial communication with ThinkGear devices.

    This class extends `ThinkGearProtocol` to implement serial communication
    protocols. It provides methods for connecting to a device via a serial interface,
    receiving data, and managing the connection lifecycle.

    Attributes:
        device (Optional[serial.Serial]): The serial connection object to the ThinkGear device.
    """

    def __init__(self, debug: bool = False):
        """
        Initialize the ThinkGearSerial instance.

        Args:
            debug (bool): Enables debugging mode if True. Defaults to False.
        """
        super().__init__(debug)
        self.device: Optional[serial.Serial] = None

    @staticmethod
    def connect_device(address: Tuple[str, int]) -> Optional[serial.Serial]:
        """
        Establish a serial connection to a ThinkGear device.

        Args:
            address (Tuple[str, int]): A tuple containing the serial port (e.g., '/dev/ttyUSB0')
                                       and the baud rate.

        Returns:
            Optional[serial.Serial]: The connected serial device object, or None if the connection fails.
        """
        device = serial.Serial(
            address[0],
            baudrate=address[1],
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            rtscts=False,
            dsrdtr=False,
        )
        return device

    def connect(self, device: Union[Tuple[str, int], serial.Serial]) -> None:
        """
        Connect to a ThinkGear device using a serial interface.

        Args:
            device (Union[Tuple[str, int], serial.Serial]): Either a tuple specifying the serial
                                                           port and baud rate, or an already initialized
                                                           `serial.Serial` object.

        Raises:
            serial.SerialException: If the connection fails when using the address tuple.
        """
        if isinstance(device, serial.Serial):
            self.device = device
        else:
            self.device = self.connect_device(device)
        if self._debug:
            print(f"Connected to device at {device}.")

    def disconnect(self) -> None:
        """
        Disconnect from the ThinkGear device.

        Closes the serial connection and sets the `device` attribute to None.
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

    def get_device(self) -> Optional[serial.Serial]:
        """
        Get current instance of serial device.

        Returns:
            serial.Serial: serial device object
        """
        return self.device

    def _recv(self, size: int = 1) -> bytes:
        """
        Receive data from the ThinkGear device via the serial interface.

        This method overrides the `_recv` method from `ThinkGearProtocol`.

        Args:
            size (int): The number of bytes to read from the serial device. Defaults to 1.

        Returns:
            bytes: The received data. Returns an empty byte string if not connected.
        """
        if self.device is None:
            if self._debug:
                print("Attempt to receive data without an active connection.")
            return b""
        data = self.device.read(size)
        if self._debug:
            print(f"Received data: {data}")
        return data
