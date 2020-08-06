import time
from thinkgear import ThinkGear, RawDataPoint

if __name__ == '__main__':
    device = ThinkGear(('0C:61:CF:29:D5:9B', 5))
    device.connect()
    if device.is_connected():
        while(True):
            data = device.read()
            if data and not isinstance(data, RawDataPoint):
                print(data)
    else:
        print("Failed to connect.")
