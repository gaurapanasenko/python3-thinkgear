from typing import List, Dict, Union, Type
from collections import namedtuple


def _eeg_from_bytes(data: bytes) -> List[int]:
    """Convert series of 3-byte unsigned integers to list of integers."""
    return [
        int.from_bytes(data[i : i + 3], byteorder="big")
        for i in range(int(len(data) / 3))
    ]


class DataPoint(namedtuple("DataPoint", "level, code, data, value")):
    """Data point, contains raw data bytes and integer value from this data."""

    SIZE = 1

    def __new__(cls, level: int, code: int, data: bytes) -> "DataPoint":
        return super().__new__(cls, level, code, data, data[0])


class UnknownDataPoint(DataPoint):
    """Unknown data point."""

    def __str__(self) -> str:
        return f"Unknown OpCode. Value: {self.value}"


class BatteryDataPoint(DataPoint):
    """Battery level data point."""

    def __str__(self) -> str:
        return f"Battery Level: {self.value}"


class PoorSignalDataPoint(DataPoint):
    """Poor signal level data point."""

    @property
    def has_contact(self) -> bool:
        """Headset has contact to skin."""
        return bool(self.value < 200)

    def __str__(self) -> str:
        string = f"Poor Signal Level: {self.value}"
        if not self.has_contact:
            string += " - NO CONTACT TO SKIN"
        return string


class AttentionDataPoint(DataPoint):
    """Attention level data point."""

    def __str__(self) -> str:
        return f"Attention Level: {self.value}"


class MeditationDataPoint(DataPoint):
    """Meditation level data point."""

    def __str__(self) -> str:
        return f"Meditation Level: {self.value}"


class BlinkDataPoint(DataPoint):
    """Blink level data point."""

    def __str__(self) -> str:
        return f"Blink Level: {self.value}"


class RawDataPoint(namedtuple("RawDataPoint", "level, code, data, value")):
    """Raw data point."""

    SIZE = 0

    def __new__(cls, level: int, code: int, data: bytes) -> "RawDataPoint":
        return super().__new__(
            cls, level, code, data, int.from_bytes(data, byteorder="big", signed=True)
        )

    def __str__(self) -> str:
        return f"Raw Value: {self.value}"


class EegDataPoints(
    namedtuple(
        "RawDataPoint",
        "level, code, data, delta, theta, lowAlpha, highAlpha, lowBeta, highBeta, lowGamma, midGamma",
    )
):
    """Electroencephalogram data points."""

    SIZE = 8

    def __new__(cls, level: int, code: int, data: bytes) -> "EegDataPoints":
        return super().__new__(cls, level, code, data, *_eeg_from_bytes(data))

    def __str__(self) -> str:
        # pylint: disable=missing-format-attribute
        return f"""EEG Powers:
                delta: {self.delta}
                theta: {self.theta}
                lowAlpha: {self.lowAlpha}
                highAlpha: {self.highAlpha}
                lowBeta: {self.lowBeta}
                highBeta: {self.highBeta}
                lowGamma: {self.lowGamma}
                midGamma: {self.midGamma}
                """


DataPointType = Union[DataPoint, RawDataPoint, EegDataPoints]

DATA_POINTS: Dict[int, Type[DataPointType]] = {
    0x01: BatteryDataPoint,
    0x02: PoorSignalDataPoint,
    0x04: AttentionDataPoint,
    0x05: MeditationDataPoint,
    0x16: BlinkDataPoint,
    0x80: RawDataPoint,
    0x83: EegDataPoints,
    0xBA: UnknownDataPoint,
    0xBC: UnknownDataPoint,
}
