from typing import Tuple, Optional, List
import socket  # type: ignore

from thinkgear.think_gear import ThinkGearProtocol

BUFFER_SIZE = 65500


class ThinkGearBluetooth(ThinkGearProtocol):
    """Bluetooth communication with Think Gear device."""

    def __init__(self, debug: bool = False):
        super().__init__(debug)
        self.socket: Optional[socket.socket] = None

    @staticmethod
    def connect_device(address: Tuple[str, int]) -> Optional[socket.socket]:
        """Connect device using address and port."""
        soc = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
        )
        soc.connect(address)
        return soc

    def connect(self, address: Tuple[str, int]) -> None:
        """Connect to device."""
        self.socket = self.connect_device(address)

    def is_connected(self) -> bool:
        """Check is connected to device."""
        return self.socket is not None

    def _recv(self) -> bytes:
        """Receive data from bluetooth device."""
        if self.socket is None:
            return b""
        return self.socket.recv(BUFFER_SIZE)


ThinkGear = ThinkGearBluetooth
