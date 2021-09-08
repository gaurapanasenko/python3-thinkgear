import unittest
from thinkgear.data_points import (
    PoorSignalDataPoint,
    EegDataPoints,
    AttentionDataPoint,
    MeditationDataPoint,
    RawDataPoint,
)
from thinkgear.parser import parse
from thinkgear.think_gear import ThinkGearProtocol

DATASHEET_EXAMPLE = b"\xaa\xaa\x20\x02\x00\x83\x18\x00\x00\x94\x00\x00\x42\x00\x00\x0b\x00\x00\x64\x00\x00\x4d\x00\x00\x3d\x00\x00\x07\x00\x00\x05\x04\x0D\x05\x3d\x34"


class ThinkGearTest(ThinkGearProtocol):
    def __init__(self):
        super().__init__()
        self.recv_data = b""

    def _recv(self) -> bytes:
        return self.recv_data


class TestParserMethods(unittest.TestCase):
    def test_parse(self):
        data = parse(DATASHEET_EXAMPLE[3:-1])
        self.assertEqual(
            list(map(type, data)),
            [
                PoorSignalDataPoint,
                EegDataPoints,
                AttentionDataPoint,
                MeditationDataPoint,
            ],
        )
        data = parse(b"\x83\x33\x34\x55")
        self.assertEqual(list(map(type, data)), [RawDataPoint])
        data = parse(b"\x03")
        self.assertEqual(list(map(type, data)), [RawDataPoint])
        data = parse(b"\x02")
        self.assertEqual(list(map(type, data)), [RawDataPoint])


class TestThinkGearMethods(unittest.TestCase):
    def test_skip_to_beginning(self):
        tg = ThinkGearTest()
        tg._buffer = bytearray(b"\xaa\xaa")
        tg.skip_to_beginning()
        self.assertEqual(tg._buffer, b"\xaa\xaa")
        tg._buffer = bytearray(b"1231\xaa\xaa")
        tg.skip_to_beginning()
        self.assertEqual(tg._buffer, b"\xaa\xaa")
        tg._buffer = bytearray(b"1231\xaa\xaa123")
        tg.skip_to_beginning()
        self.assertEqual(tg._buffer, b"\xaa\xaa123")
        tg._buffer = bytearray(b"")
        tg.skip_to_beginning()
        self.assertEqual(tg._buffer, b"")
        tg._buffer = bytearray(b"\x00")
        tg.skip_to_beginning()
        self.assertEqual(tg._buffer, b"\x00")
        tg._buffer = bytearray(b"\x00\x01")
        tg.skip_to_beginning()
        self.assertEqual(tg._buffer, b"\x01")

    def test_pop_packet(self):
        tg = ThinkGearTest()
        tg.recv_data = b""
        self.assertEqual(tg.pop_packet(), b"")
        tg.recv_data = b"\x00"
        self.assertEqual(tg.pop_packet(), b"")
        tg.recv_data = b"\x00\xaa\xaa"
        self.assertEqual(tg.pop_packet(), b"")
        tg._buffer = bytearray()
        tg.recv_data = b"\xaa\xaa\x00\xaa\xaa\x01\x34\xcb"
        self.assertEqual(tg.pop_packet(), b"\x34")
        tg.recv_data = b"\xaa\xaa\x01\x23\x00\xaa\xaa\x01\x34\xcb"
        self.assertEqual(tg.pop_packet(), b"\x34")
        tg.recv_data = b"\xaa\xaa\x10"
        self.assertEqual(tg.pop_packet(), b"")
        tg._buffer = bytearray()
        tg.recv_data = b"\xaa\xaa\x02\x00\x00\xff"
        self.assertEqual(tg.pop_packet(), b"\x00\x00")
        tg.recv_data = DATASHEET_EXAMPLE[:]
        self.assertEqual(tg.pop_packet(), DATASHEET_EXAMPLE[3:-1])


if __name__ == "__main__":
    unittest.main()
