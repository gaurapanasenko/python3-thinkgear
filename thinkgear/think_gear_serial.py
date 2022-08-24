from typing import Tuple, Optional, List, Union
import serial  # type: ignore

from thinkgear.think_gear import ThinkGearProtocol

BUFFER_SIZE = 65500


class ThinkGearSerial(ThinkGearProtocol):
    """Serial communication with Think Gear device."""

    def __init__(self, debug: bool = False):
        super().__init__(debug)
        self.device: Optional[serial.Serial] = None

    @staticmethod
    def connect_device(address: Tuple[str, int]) -> Optional[serial.Serial]:
        """Connect device using path."""
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
        """Connect to device."""
        if isinstance(device, serial.Serial):
            self.device = device
        else:
            self.device = self.connect_device(device)

    def is_connected(self) -> bool:
        """Check is connected to device."""
        return self.device is not None

    def _recv(self) -> bytes:
        """Receive data from bluetooth device."""
        if self.device is None:
            return b""
        return self.device.read(BUFFER_SIZE)
