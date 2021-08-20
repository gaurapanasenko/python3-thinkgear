from typing import Tuple, Optional, List

import bluetooth


from thinkgear.parser import parse
from thinkgear.data_points import DataPointType

START_OF_PACKET = b"\xaa\xaa"

BUFFER_SIZE = 4096


def discover(lookup_name: str = "MindWave") -> Optional[Tuple[str, int]]:
    """Find some device by name."""
    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    for address, name in nearby_devices:
        if lookup_name in name:
            services = bluetooth.find_service(address=address)
            try:
                port = next(
                    i["port"]
                    for i in services
                    if i["protocol"] == "RFCOMM" and i["port"]
                )
                return (address, port)
            except StopIteration:
                pass
    return None


def connect(
    address: Optional[Tuple[str, int]] = None
) -> Optional[bluetooth.BluetoothSocket]:
    """Connect device using address and port."""
    if address is None:
        address = discover()

    if address is None:
        return None

    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        socket.connect(address)
    except bluetooth.btcommon.BluetoothError:
        return None
    return socket


def _check_sum(payload: bytes, check_sum: int) -> bool:
    return (~(sum(payload) % 256)) + 256 == check_sum


class ThinkGear:
    """Read data by ThinkGear Serial Stream Protocol."""

    def __init__(self, address: Optional[Tuple[str, int]] = None):
        self._address: Optional[Tuple[str, int]] = address
        self._buffer: bytearray = bytearray()
        self.socket: Optional[bluetooth.BluetoothSocket] = None
        self._data_points: List[DataPointType] = []

    def connect(self) -> None:
        """Connect to device."""
        self.socket = connect(self._address)

    def is_connected(self) -> bool:
        """Check is connected to device."""
        return self.socket is not None

    def read(self) -> DataPointType:
        """Read one data point."""
        if len(self._data_points) <= 0:
            self._data_points = self.readall()
        return self._data_points.pop()

    def readall(self) -> List[DataPointType]:
        """Read bunch of data points."""
        if self.socket is None:
            return []

        data = self.socket.recv(BUFFER_SIZE)
        if not data:
            return []

        self._buffer += data

        data_points = self._data_points
        self._data_points = []

        while len(self._buffer) >= 3:
            # Go to start of packet
            if not self._buffer.startswith(START_OF_PACKET):
                del self._buffer[0]
                continue

            size = self._buffer[2]

            if not size or size < 0:
                # got bad size, ignore this packet
                del self._buffer[:2]
                continue

            if size + 4 > len(self._buffer):
                # there is not enough data in buffer, exit
                break

            packet = self._buffer[3 : size + 3]
            check_sum = self._buffer[size + 3]
            del self._buffer[: size + 4]

            if _check_sum(packet, check_sum):
                data_points += parse(packet)

        if not data_points:
            raise BlockingIOError("No data points")

        return data_points
