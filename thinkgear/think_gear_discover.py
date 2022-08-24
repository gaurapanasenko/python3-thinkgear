from typing import Tuple, Optional, List
import bluetooth


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
