from typing import Any, Tuple, Optional

try:
    from bluetooth import discover_devices, find_service
except AttributeError:

    def discover_devices(*args: Any, **kwargs: Any) -> Optional[list[Any]]:
        raise NotImplementedError("Failed to import bluetooth")

    def find_service(*args: Any, **kwargs: Any) -> list[Any]:
        raise NotImplementedError("Failed to import bluetooth")


__all__ = ("discover",)


def discover(lookup_name: str = "MindWave") -> Optional[Tuple[str, int]]:
    """
    Discover a Bluetooth device by name and retrieve its RFCOMM service details.

    This function scans for nearby Bluetooth devices and attempts to locate one
    with a name containing the specified `lookup_name`. If a matching device is
    found, it searches for an RFCOMM service on the device and returns its address
    and port.

    Args:
        lookup_name (str): The name or part of the name of the target Bluetooth device.
                          Defaults to "MindWave".

    Returns:
        Optional[Tuple[str, int]]: A tuple containing the Bluetooth address and RFCOMM port
                                   of the discovered device, or None if no matching device
                                   or service is found.
    """
    # Discover nearby Bluetooth devices and their names
    nearby_devices = discover_devices(lookup_names=True)

    # Iterate through each discovered device
    for address, name in nearby_devices:
        if lookup_name in name:  # Check if the device name matches the target name
            services = find_service(address=address)  # Fetch services for the device

            # Search for an RFCOMM service and extract its port
            try:
                port = next(
                    i["port"]
                    for i in services
                    if i["protocol"] == "RFCOMM" and i["port"]
                )
                return (address, port)  # Return the device address and port if found
            except StopIteration:
                pass  # Continue searching if no RFCOMM service with a port is found

    # Return None if no matching device or service is found
    return None
