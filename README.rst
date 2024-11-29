ThinkGear Serial Stream Protocol Implementation
===============================================

Installation
------------

To use ThinkGear, first install it using pip:

.. code-block:: console

   (.venv) $ pip install thinkgear-py3
   (.venv) $ pip install pybluez2  # For Bluetooth discovery
   (.venv) $ pip install pyserial  # For serial communication

Using Serial Communication
--------------------------

For connecting via a serial port, such as COM1 at a speed of 57600 baud, you can use the `ThinkGearSerial` class. The following examples demonstrate how to read and print `PoorSignal`, `Attention`, and `Meditation` data points.

Example for Windows
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from thinkgear.serial import ThinkGearSerial
   from thinkgear import PoorSignalDataPoint, MeditationDataPoint, AttentionDataPoint

   # Create an instance of ThinkGearSerial
   t = ThinkGearSerial()

   # Connect to the device (e.g., COM1 at 57600 baud)
   t.connect(("COM1", 57600))

   # Continuously read and process data
   while True:
       for data_point in t.read():
           if isinstance(data_point, PoorSignalDataPoint):
               print("Poor signal:", data_point.value)
           elif isinstance(data_point, AttentionDataPoint):
               print("Attention:", data_point.value)
           elif isinstance(data_point, MeditationDataPoint):
               print("Meditation:", data_point.value)

Example for Linux
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from thinkgear.serial import ThinkGearSerial
   from thinkgear import PoorSignalDataPoint, MeditationDataPoint, AttentionDataPoint

   # Create an instance of ThinkGearSerial
   t = ThinkGearSerial()

   # Connect to the device (e.g., /dev/ttyUSB0 at 57600 baud)
   t.connect(("/dev/ttyUSB0", 57600))

   # Continuously read and process data
   while True:
       for data_point in t.read():
           if isinstance(data_point, PoorSignalDataPoint):
               print("Poor signal:", data_point.value)
           elif isinstance(data_point, AttentionDataPoint):
               print("Attention:", data_point.value)
           elif isinstance(data_point, MeditationDataPoint):
               print("Meditation:", data_point.value)

Using Bluetooth Communication
-----------------------------

For Bluetooth communication, you can discover and connect to a ThinkGear device. The following steps demonstrate how to discover a Bluetooth device and establish a connection.

Device Discovery
~~~~~~~~~~~~~~~~

You can discover nearby Bluetooth devices with a specific name, such as `MyndBand`.

.. code-block:: python

   from thinkgear.discover import discover

   # Discover a device with the name containing "MyndBand"
   device_info = discover("MyndBand")
   print(device_info)  # Example output: ('XX:XX:XX:XX:XX:XX', 5)

**Note**: Device discovery is a slow operation. It is good practice to save the discovered device's address and port for future connections.

Connecting to a Bluetooth Device
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have the device's address and port, you can use `ThinkGearBluetooth` to connect and process data points.

.. code-block:: python

   from thinkgear.bluetooth import ThinkGearBluetooth
   from thinkgear import PoorSignalDataPoint, MeditationDataPoint, AttentionDataPoint

   # Create an instance of ThinkGearBluetooth
   t = ThinkGearBluetooth()

   # Use the discovered device information (address and port)
   device_info = ('XX:XX:XX:XX:XX:XX', 5)
   t.connect(device_info)

   # Continuously read and process data
   while True:
       for data_point in t.read():
           if isinstance(data_point, PoorSignalDataPoint):
               print("Poor signal:", data_point.value)
           elif isinstance(data_point, AttentionDataPoint):
               print("Attention:", data_point.value)
           elif isinstance(data_point, MeditationDataPoint):
               print("Meditation:", data_point.value)

Notes
-----

- When using serial communication on Windows, ensure that the COM port (e.g., `COM1`) is correctly configured.
- On Linux, ensure you have the appropriate permissions to access the serial port (e.g., `/dev/ttyUSB0`). This might involve adding your user to the `dialout` group or running the program with `sudo`.
- Bluetooth discovery is time-consuming. Save the device's address and port once discovered to avoid repeated discovery operations.
