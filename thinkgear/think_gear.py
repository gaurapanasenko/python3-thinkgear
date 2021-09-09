from typing import Tuple, Optional, List

import bluetooth


from thinkgear.parser import parse
from thinkgear.data_points import DataPointType, RawDataPoint

START_OF_PACKET = b"\xaa\xaa"
START_OF_PACKET_SIZE = len(START_OF_PACKET)

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


def _check_sum(payload: bytes, check_sum: int) -> bool:
    return (~(sum(payload) & 0xFF) & 0xFF) == check_sum


class ThinkGearProtocol:
    """Read data by ThinkGear Serial Stream Protocol."""

    def __init__(self) -> None:
        self._buffer: bytearray = bytearray()
        self._data_points: List[DataPointType] = []

    def _recv(self) -> bytes:
        """Receive from device."""
        return b""

    def read(self) -> Optional[DataPointType]:
        """Read one data point."""
        if len(self._data_points) <= 0:
            self._data_points = self.readall()
        if len(self._data_points) <= 0:
            return None
        return self._data_points.pop()

    def skip_to_beginning(self) -> None:
        """Find beginning of packet."""
        data_beginning = self._buffer.find(START_OF_PACKET)
        self._buffer = self._buffer[data_beginning:]

    def pop_packet(self, recv: bool = True) -> bytes:
        """Get data from one packet."""
        if recv:
            self._buffer += self._recv()

        while True:
            self.skip_to_beginning()

            if len(self._buffer) < 3:
                # there is not enough data in buffer, exit
                return b""

            size = self._buffer[2]
            if size <= 0:
                # got bad size
                del self._buffer[0]
                continue

            if size + 4 > len(self._buffer):
                # there is not enough data in buffer, exit
                return b""

            packet = self._buffer[3 : size + 3]
            check_sum = self._buffer[size + 3]
            del self._buffer[: size + 4]

            if not _check_sum(packet, check_sum):
                continue

            return packet

        return b""

    def pop(self, recv: bool = True) -> List[DataPointType]:
        return parse(self.pop_packet(recv))

    def readall(self) -> List[DataPointType]:
        """Read bunch of data points."""
        self._buffer += self._recv()

        data_points = self._data_points
        self._data_points = []
        points: List[DataPointType] = [RawDataPoint(0, 0, b"")]

        while points:
            points = self.pop(False)
            data_points += points

        if not data_points:
            raise BlockingIOError("No data points")

        return data_points


class ThinkGearBluetooth(ThinkGearProtocol):
    """Bluetooth communication with Think Gear device."""

    def __init__(self, address: Optional[Tuple[str, int]] = None):
        super().__init__()
        self._address: Optional[Tuple[str, int]] = address
        self.socket: Optional[bluetooth.BluetoothSocket] = None

    @staticmethod
    def connect_device(
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

    def connect(self) -> None:
        """Connect to device."""
        self.socket = self.connect_device(self._address)

    def is_connected(self) -> bool:
        """Check is connected to device."""
        return self.socket is not None

    def _recv(self) -> bytes:
        """Receive data from bluetooth device."""
        if self.socket is None:
            return b""
        return self.socket.recv(BUFFER_SIZE)


ThinkGear = ThinkGearBluetooth
