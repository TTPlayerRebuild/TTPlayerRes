"""One-time, lossless import of the supplied 5.7.9 application-root ttpres.dll."""
import argparse
import io
import struct
import zipfile
from pathlib import Path
from resource_model import CODECS, resources, save_json, sha256, source_payload

BASELINE = '866726b4c9b712ef0cb5492a74d05bbb15a97f8f47595d743dcf268aa25853a5'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dll', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    data = args.dll.read_bytes()
    if sha256(data) != BASELINE:
        raise ValueError('Expected the unmodified application-root 5.7.9 DLL')
    if args.output.exists() and any(args.output.iterdir()):
        raise ValueError('Import destination must be empty (never overwrite edited source)')
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = dict(schema=1, baseline_sha256=BASELINE, resources=[])
    folders = {4:'menus', 5:'dialogs', 6:'strings', 241:'toolbars'}
    for (kind, name, language), raw, codepage in resources(data):
        slug = f'{name}-{language}'
        item = dict(type=kind, name=name, language=language, codepage=codepage,
                    original_size=len(raw), original_sha256=sha256(raw))
        if kind in CODECS:
            item.update(format='json', source=f'{folders[kind]}/{slug}.json')
            save_json(args.output / item['source'], CODECS[kind][0](raw))
        else:
            content = raw
            if kind == 2:
                item.update(format='bmp', source=f'bitmaps/{slug}.bmp')
                header_size = struct.unpack_from('<I', raw)[0]
                bpp = struct.unpack_from('<H', raw, 14)[0]
                compression, colors = struct.unpack_from('<I', raw, 16)[0], struct.unpack_from('<I', raw, 32)[0]
                colors = colors or ((1 << bpp) if bpp <= 8 else 0)
                bits = 14 + header_size + 4 * colors + (12 if header_size == 40 and compression == 3 else 0)
                content = struct.pack('<2sIHHI', b'BM', len(raw)+14, 0, 0, bits) + raw
            elif kind == 'ZIP':
                stem = name.strip('<>').lower()
                item.update(format='zip', source=f'skins/{stem}.zip', directory=f'skins/{stem}')
                with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                    for entry in archive.infolist():
                        relative = Path(entry.filename)
                        if relative.is_absolute() or '..' in relative.parts or ':' in entry.filename:
                            raise ValueError('Unsafe original ZIP path')
                    archive.extractall(args.output / item['directory'])
            else:
                item.update(format='raw', source=f'raw/{kind}-{slug}.bin')
            path = args.output / item['source']
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        if source_payload(args.output, item) != raw:
            raise ValueError(f'Resource did not round-trip exactly: {kind}/{name}/{language}')
        manifest['resources'].append(item)
    save_json(args.output / 'manifest.json', manifest)
    print(f'Imported and byte-verified {len(manifest["resources"])} resources')


if __name__ == '__main__':
    main()
