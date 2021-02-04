from typing import List


_crc_table = None


def _get_table() -> List[int]:
    global _crc_table
    if not _crc_table:
        _crc_table = _crc_init()

    return _crc_table


def calc_crc(bytelist: List[int]) -> int:
    crc_table = _get_table()

    crc = 0xFF

    for byte in bytelist:
        # print((crc ^ byte) & 255)
        crc = crc_table[(crc ^ byte) & 255]

    return (~crc) & 255


def _crc_init() -> List[int]:
    crc_table = []

    for i in range(0, 0x100):
        crc = i

        for bit in range(0, 8):
            crc = (crc << 1) ^ 0x1D if crc & 0x80 else crc << 1

        crc_table.append(crc)

    return crc_table
