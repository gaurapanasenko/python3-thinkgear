from typing import List
from thinkgear.data_points import DATA_POINTS, DataPointType, RawDataPoint


EXCODE: int = 0x55


def _create_data_point(level: int, code: int, data: bytes) -> DataPointType:
    point_type = DATA_POINTS.get(code, RawDataPoint)
    if len(data) < point_type.SIZE:
        point_type = RawDataPoint
    return point_type(level, code, data)


def parse(payload: bytes) -> List[DataPointType]:
    """Parse packet from ThinkGear Serial Stream.
    http://wearcam.org/ece516/mindset_communications_protocol.pdf"""
    pLength = len(payload)
    bytesParsed = 0
    code = 0
    length = 0
    extendedCodeLevel = 0
    data_points: List[DataPointType] = []

    # Loop until all bytes are parsed from the payload[] array...
    while bytesParsed < pLength:
        # Parse the extendedCodeLevel, code, and length
        extendedCodeLevel = 0
        while payload[bytesParsed] == EXCODE:
            extendedCodeLevel += 1
            bytesParsed += 1
        code = payload[bytesParsed]
        bytesParsed += 1
        # ~ if code & 0x80 and code not in [0xBA, 0xBC]:
        if code in [0x80, 0x83]:
            length = payload[bytesParsed]
            bytesParsed += 1
        else:
            length = 1

        data = payload[bytesParsed : bytesParsed + length]
        data_points.append(_create_data_point(extendedCodeLevel, code, data))

        bytesParsed += length
    return data_points
