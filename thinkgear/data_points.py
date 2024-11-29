from typing import List, Dict, Union, Type
from collections import namedtuple


__all__ = (
    "DataPoint",
    "BatteryDataPoint",
    "PoorSignalDataPoint",
    "AttentionDataPoint",
    "MeditationDataPoint",
    "BlinkDataPoint",
    "RawDataPoint",
    "EegDataPoints",
    "UnknownDataPoint",
    "DataPointType",
    "DATA_POINTS",
)


def _eeg_from_bytes(data: bytes) -> List[int]:
    """
    Convert a sequence of 3-byte unsigned integers into a list of integers.

    Args:
        data (bytes): The raw bytes representing 3-byte unsigned integers.

    Returns:
        List[int]: A list of integers extracted from the input data.
    """
    return [
        int.from_bytes(data[i : i + 3], byteorder="big")
        for i in range(int(len(data) / 3))
    ]


class DataPoint(namedtuple("DataPoint", "level, code, data, value")):
    """
    Base class for data points, containing raw data bytes and an interpreted value.

    Attributes:
        level (int): The EXCODE level.
        code (int): The operation code for the data point.
        data (bytes): The raw data bytes.
        value (int): The interpreted value extracted from the data.
    """

    SIZE = 1

    def __new__(cls, level: int, code: int, data: bytes) -> "DataPoint":
        """
        Create a new instance of DataPoint.

        Args:
            level (int): EXCODE level.
            code (int): Operation code.
            data (bytes): Raw data bytes.

        Returns:
            DataPoint: A new instance of DataPoint.
        """
        return super().__new__(cls, level, code, data, data[0])


class UnknownDataPoint(DataPoint):
    """Represents an unknown data point."""

    def __str__(self) -> str:
        return f"Unknown OpCode. Value: {self.value}"


class BatteryDataPoint(DataPoint):
    """Represents a battery level data point."""

    def __str__(self) -> str:
        return f"Battery Level: {self.value}"


class PoorSignalDataPoint(DataPoint):
    """Represents a poor signal level data point."""

    @property
    def has_contact(self) -> bool:
        """
        Check if the headset has proper contact with the skin.

        Returns:
            bool: True if contact is good, False otherwise.
        """
        return self.value < 200

    def __str__(self) -> str:
        string = f"Poor Signal Level: {self.value}"
        if not self.has_contact:
            string += " - NO CONTACT TO SKIN"
        return string


class AttentionDataPoint(DataPoint):
    """Represents an attention level data point."""

    def __str__(self) -> str:
        return f"Attention Level: {self.value}"


class MeditationDataPoint(DataPoint):
    """Represents a meditation level data point."""

    def __str__(self) -> str:
        return f"Meditation Level: {self.value}"


class BlinkDataPoint(DataPoint):
    """Represents a blink level data point."""

    def __str__(self) -> str:
        return f"Blink Level: {self.value}"


class RawDataPoint(namedtuple("RawDataPoint", "level, code, data, value")):
    """
    Represents a raw data point, which contains unprocessed signal data.

    Attributes:
        level (int): The EXCODE level.
        code (int): The operation code.
        data (bytes): The raw data bytes.
        value (int): The interpreted raw signal value.
    """

    SIZE = 0

    def __new__(cls, level: int, code: int, data: bytes) -> "RawDataPoint":
        """
        Create a new instance of RawDataPoint.

        Args:
            level (int): EXCODE level.
            code (int): Operation code.
            data (bytes): Raw data bytes.

        Returns:
            RawDataPoint: A new instance of RawDataPoint.
        """
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
    """
    Represents EEG data points, including power levels for various brainwave frequencies.

    Attributes:
        delta (int): Power of delta waves.
        theta (int): Power of theta waves.
        lowAlpha (int): Power of low-alpha waves.
        highAlpha (int): Power of high-alpha waves.
        lowBeta (int): Power of low-beta waves.
        highBeta (int): Power of high-beta waves.
        lowGamma (int): Power of low-gamma waves.
        midGamma (int): Power of mid-gamma waves.
    """

    SIZE = 8

    def __new__(cls, level: int, code: int, data: bytes) -> "EegDataPoints":
        """
        Create a new instance of EegDataPoints.

        Args:
            level (int): EXCODE level.
            code (int): Operation code.
            data (bytes): Raw EEG data bytes.

        Returns:
            EegDataPoints: A new instance of EegDataPoints.
        """
        return super().__new__(cls, level, code, data, *_eeg_from_bytes(data))

    def __str__(self) -> str:
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
