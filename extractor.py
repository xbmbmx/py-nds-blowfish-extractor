import argparse
from enum import Enum
from pathlib import Path

key_table_length=0x1048  # https://problemkaputt.de/gbatek.htm
byte_size=8

class ErrorCode(Enum):
    FILE_NOT_FOUND = 1
    FILE_ALREADY_EXISTS = 2
    INVALID_START_ADDRESS = 3
    FILE_TOO_SHORT = 4
    FATAL = -1


def main(startaddress: int, biosfile: Path, outfile: Path) -> None:
    print(f'Reading [ {hex(key_table_length)} ] bytes of data from [ {biosfile} ] to [ {outfile} ], starting at [ {hex(startaddress)} ]')

    if (biosfile.stat().st_size * byte_size - startaddress < key_table_length):
        print(f'The presented BIOS file is not long enough to contain the keys starting from the given address')
        print(f'Available bytes: [ {biosfile.stat().st_size * byte_size - startaddress} ], required bytes: [ {key_table_length} ]')
        exit(ErrorCode.FILE_TOO_SHORT.value)

    outfile.touch(exist_ok=True)

    with biosfile.open(mode='r+b') as biosfile, outfile.open(mode='w+b') as outfile:
        biosfile.seek(startaddress)
        keys=biosfile.read(key_table_length)
        outfile.write(keys)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Extract blowfish keys from dumped DS/DSi BIOS files'
            )

    parser.add_argument('-s', '--startaddress', type=str, help='The address to start reading from, in HEX (0xFF) or INT (255)', required=True)
    parser.add_argument('-b', '--biosfile', type=str, help='The BIOS file to read the keys from', required=True)
    parser.add_argument('-o', '--outfile', type=str, default='./blowfish-keys.bin', help='The file to output the extracted keys to', required=False)
    parser.add_argument('-f', '--force', help='Overwrite the output file if already present', action='store_true', required=False)
    args = parser.parse_args()
    
    startaddress=0

    try:
        if (args.startaddress[:2] == '0x'):
            upper_address = '0x' + args.startaddress[2:].upper()
            startaddress=int(upper_address, 16)
        else:
            startaddress=int(args.startaddress, 10)
    except ValueError:
        print(f'The provided startaddress [ {args.startaddress} ] is invalid.')
        exit(ErrorCode.INVALID_START_ADDRESS.value)


    biosfile=Path(args.biosfile)
    outfile=Path(args.outfile)

    force=args.force

    # Argument validation code

    if (not biosfile.exists()) or (not biosfile.is_file()):
        print(f'Presented biosfile [ {biosfile} ] does not exist or is not a file.')
        exit(ErrorCode.FILE_NOT_FOUND.value)

    if outfile.is_file() and not args.force:
        print(f'Output file [ {outfile} ] already exists, define -f/--force to overwrite.')
        exit(ErrorCode.FILE_ALREADY_EXISTS.value)

    # Call the main code with parameters

    main(startaddress, biosfile, outfile)
