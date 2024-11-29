from typing import List
from thinkgear.parser import parse
from thinkgear.data_points import DataPointType

SYNC = 0xAA
EXCODE = 0x55


class ThinkGearProtocol:
    """
    A base class to interface with ThinkGear devices using the ThinkGear Serial Stream Protocol.

    This class provides methods to read and parse data transmitted by ThinkGear devices.
    It is intended as an abstract class and should be subclassed to implement the `_recv` method for
    actual device communication.

    Attributes:
        _debug (bool): Flag to enable or disable debug mode. If enabled, additional debugging
                      information may be printed or logged.
    """

    def __init__(self, debug: bool = False) -> None:
        """
        Initialize the ThinkGearProtocol instance.

        Args:
            debug (bool): If True, enables debugging mode for additional logging. Defaults to False.
        """
        self._debug: bool = debug

    def _recv(self, size: int = 1) -> bytes:
        """
        Abstract method for receiving bytes from the device.

        This method must be overridden by subclasses to implement actual communication
        with the ThinkGear device.

        Args:
            size (int): The number of bytes to read. Defaults to 1.

        Returns:
            bytes: The received bytes.

        Raises:
            NotImplementedError: If this method is not overridden in a subclass.
        """
        raise NotImplementedError("The _recv method must be implemented by subclasses.")

    def read(self) -> List[DataPointType]:
        """
        Read and parse a single data payload from the ThinkGear device.

        The method synchronizes on the SYNC bytes, validates the payload length,
        calculates a checksum, and verifies it against the received checksum.
        The payload is parsed into a list of data points.

        Returns:
            List[DataPointType]: A list of parsed data points, or an empty list if parsing fails.

        Raises:
            IOError: If the full payload cannot be read.
        """
        while True:
            # Synchronize on [SYNC] bytes
            for _ in range(2):
                c = self._recv()[0]
                if c != SYNC:
                    if self._debug:
                        print("Failed to synchronize on SYNC byte.")
                    continue

            # Parse [PLENGTH] byte
            while True:
                pLength = self._recv()[0]
                if pLength != SYNC:
                    break

            if pLength > 169:
                if self._debug:
                    print(f"Invalid payload length: {pLength}.")
                continue

            # Collect [PAYLOAD...] bytes
            payload = self._recv(pLength)
            if len(payload) != pLength:
                raise IOError("Did not receive the full payload.")

            # Compute [PAYLOAD...] checksum
            checksum = sum(payload) & 0xFF
            checksum = ~checksum & 0xFF

            # Parse [CKSUM] byte
            received_checksum = self._recv()[0]

            # Verify [PAYLOAD...] checksum against [CKSUM]
            if received_checksum != checksum:
                if self._debug:
                    print(
                        f"Checksum mismatch: calculated={checksum}, received={received_checksum}."
                    )
                continue
            return parse(payload)
