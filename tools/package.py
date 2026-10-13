"""Package only the verified DLL and its checksum; never private tests/source."""
import argparse
import zipfile
from pathlib import Path
from audit import audit
from compile_resources import validate_version
from resource_model import load_json, sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    version = validate_version(args.version)
    dll = args.directory / 'ttpres.dll'
    report = audit(dll, load_json(source / 'resources/original/manifest.json'))
    if report['version'] != version:
        raise ValueError('Recompile before changing the package version')
    data = dll.read_bytes()
    name = f'ttpres-{version}.zip'
    path = args.directory / name
    temporary = path.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        stamp = (2026, 1, 1, 0, 0, 0)
        for entry, payload in [('ttpres.dll', data), ('SHA256SUMS.txt', f'{sha256(data)}  ttpres.dll\n'.encode('ascii'))]:
            info = zipfile.ZipInfo(entry, stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            package.writestr(info, payload)
    temporary.replace(path)
    (args.directory / 'SHA256SUMS.txt').write_text(f'{sha256(path.read_bytes())}  {name}\n', encoding='ascii')
    print(f'Package: {path}')


if __name__ == '__main__':
    main()
