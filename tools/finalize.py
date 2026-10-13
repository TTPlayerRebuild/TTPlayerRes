"""Write the original player's integrity field after the linker has finished."""
import argparse
import struct
from pathlib import Path
from resource_model import legacy_checksum


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dll', type=Path)
    args = parser.parse_args()
    data = bytearray(args.dll.read_bytes())
    checksum = legacy_checksum(data)
    if struct.unpack_from('<I', data, 0x20)[0] != checksum:
        struct.pack_into('<I', data, 0x20, checksum)
        args.dll.write_bytes(data)
    print(f'Original 5.7.9 resource integrity field: {checksum:08X}')


if __name__ == '__main__':
    main()
