from typing import List, Dict
from collections import namedtuple


def _eeg_from_bytes(data: bytes) -> List[int]:
    """Convert series of 3-byte unsigned integers to list of integers."""
    return [
        int.from_bytes(data[i : i + 3], byteorder="big")
        for i in range(int(len(data) / 3))
    ]


class DataPoint(namedtuple("DataPoint", "data, value")):
    """Data point, contains raw data bytes and integer value from this data."""

    def __new__(cls, data):
        return super().__new__(cls, data, data[0])


class UnknownDataPoint(DataPoint):
    """Unknown data point."""

    def __str__(self):
        return f"Unknown OpCode. Value: {self.value}"


class PoorSignalDataPoint(DataPoint):
    """Poor signal level data point."""

    @property
    def has_contact(self):
        """Headset has contact to skin."""
        return self.value < 200

    def __str__(self):
        string = f"Poor Signal Level: {self.value}"
        if not self.has_contact:
            string += " - NO CONTACT TO SKIN"
        return string


class AttentionDataPoint(DataPoint):
    """Attention level data point."""

    def __str__(self):
        return f"Attention Level: {self.value}"


class MeditationDataPoint(DataPoint):
    """Meditation level data point."""

    def __str__(self):
        return f"Meditation Level: {self.value}"


class BlinkDataPoint(DataPoint):
    """Blink level data point."""

    def __str__(self):
        return f"Blink Level: {self.value}"


class RawDataPoint(namedtuple("RawDataPoint", "data, value")):
    """Raw data point."""

    def __new__(cls, data):
        return super().__new__(
            cls, data, int.from_bytes(data, byteorder="big", signed=True)
        )

    def __str__(self):
        return f"Raw Value: {self.value}"


class EegDataPoints(
    namedtuple(
        "RawDataPoint",
        "data, delta, theta, lowAlpha, highAlpha, lowBeta, highBeta, lowGamma, midGamma",
    )
):
    """Electroencephalogram data points."""

    def __new__(cls, data):
        return super().__new__(cls, data, *_eeg_from_bytes(data))

    def __str__(self):
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


DATA_POINTS: Dict[int, type] = {
    0x02: PoorSignalDataPoint,
    0x04: AttentionDataPoint,
    0x05: MeditationDataPoint,
    0x16: BlinkDataPoint,
    0x80: RawDataPoint,
    0x83: EegDataPoints,
    0xBA: UnknownDataPoint,
    0xBC: UnknownDataPoint,
}
