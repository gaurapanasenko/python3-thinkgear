import collections


from thinkgear.parser import parse
from thinkgear.reader import connect


START_OF_PACKET = b'\xaa\xaa'


def _check_sum(payload, check_sum):
    return (~(sum(payload) % 256)) + 256 == ord(check_sum)


class ThinkGear:
    """Read data by ThinkGear Serial Stream Protocol."""
    def __init__(self, address=None):
        self._address = address
        self._reader = None
        self.socket = None
        self._data_points = collections.deque()

    def connect(self):
        """Connect to device."""
        self._reader, self.socket = connect(self._address)

    def is_connected(self):
        """Check is connected to device."""
        return self._reader is not None

    def read(self):
        """Read one data point."""
        if len(self._data_points) <= 0:
            data_points = self._read_data_points()
            self._data_points.extend(data_points)
        if not self._data_points:
            return None
        return self._data_points.pop()

    def _read_data_points(self):
        data_points = []
        # Go to start of packet
        while True:
            peek = self._reader.peek(3)
            if not peek or len(peek) < 3:
                return data_points
            if not peek.startswith(START_OF_PACKET):
                self._reader.read(1)
                continue

            assert len(peek) > 2
            size = peek[2]

            if not size or size < 0:
                # got bad size, ignore this packet
                self._reader.read(3)
                return data_points

            assert size > 0
            peek = self._reader.peek(size + 4)

            if size + 4 > len(peek):
                # there is not enough data in buffer, exit
                return data_points

            self._reader.read(3)
            packet = self._reader.read(size)
            check_sum = self._reader.read(1)

            if _check_sum(packet, check_sum):
                data_points += parse(packet)
