from typing import Tuple

import bluetooth


def discover(lookup_name: str = "MindWave"):
    """Find some device by name."""
    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    for address, name in nearby_devices:
        if lookup_name in name:
            services = bluetooth.find_service(address=address)
            try:
                port = next(i['port'] for i in services
                            if i['protocol'] == 'RFCOMM' and i['port'])
                return (address, port)
            except StopIteration:
                pass
    return None


def connect(address: Tuple[str, int] = None):
    """Connect device using address and port."""
    if address is None:
        address = discover()

    if address is None:
        return (None, None)

    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        socket.connect(address)
    except bluetooth.btcommon.BluetoothError:
        return (None, None)
    return _Reader(socket), socket


class _Reader:
    def __init__(self, socket):
        self.socket = socket
        self.buffer = b""

    def read(self, size: int = 1):
        """Read bytes by size."""
        self._fill_buffer(size)
        out_buffer = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return out_buffer

    def peek(self, size: int = 1):
        """Peek bytes by size."""
        self._fill_buffer(size)
        return self.buffer[:size]

    def _fill_buffer(self, size: int):
        missed_size = size - len(self.buffer)
        if missed_size > 0:
            self.buffer += self.socket.recv(missed_size)
