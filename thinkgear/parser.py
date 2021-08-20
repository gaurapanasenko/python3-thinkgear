from typing import List
from thinkgear.data_points import DATA_POINTS, DataPointType, RawDataPoint


EXTENDED_CODE_BYTE: int = 0x55


def _create_data_point(code: int, data: bytes) -> DataPointType:
    point_type = DATA_POINTS.get(code, RawDataPoint)
    if len(data) < point_type.SIZE:
        return RawDataPoint(data)
    return point_type(data)


def parse(packet: bytes) -> List[DataPointType]:
    """Parse packet from ThinkGear Serial Stream."""
    parser = _Parser(packet)
    data_points = []
    while parser:
        data_points.append(parser.pop_data_point())
    return data_points


class _Parser:
    """Parses byte data from ThinkGear Serial Stream."""

    def __init__(self, packet: bytes):
        self._packet: bytes = packet
        self._index: int = 0

    def __bool__(self) -> bool:
        return not self._index == len(self._packet)

    def pop_data_point(self) -> DataPointType:
        """Pop one data point from packet."""
        code = self._pop_code()
        return _create_data_point(code, self._pop_data(code))

    def _pop_code(self) -> int:
        # EXTENDED_CODE_BYTES seem not to be used according to
        # http://wearcam.org/ece516/mindset_communications_protocol.pdf
        # (August 2012)
        # so we ignore them
        while True:
            code = ord(self._pop_bytes())
            if code != EXTENDED_CODE_BYTE:
                return code

    def _pop_bytes(self, size: int = 1) -> bytes:
        index = self._index
        self._index += size
        return self._packet[index : index + size]

    def _pop_data(self, code: int) -> bytes:
        size = self._pop_length(code)
        if size == -1:
            return b""
        return self._pop_bytes(size)

    def _pop_length(self, code: int) -> int:
        # If code is one of the mysterious initial code values
        # return before the extended code check
        if code == 0xBA or code == 0xBC or code <= 0x7F:
            return 1
        byte = self._pop_bytes()
        if len(byte) != 1:
            return -1
        return ord(self._pop_bytes())
