"""Compile editable original sources to a .res file; emit extension metadata."""
import argparse
import datetime
import json
import re
import struct
from pathlib import Path
from resource_model import original_entries, res_file, save_json, sha256


def validate_version(version):
    match = re.fullmatch(r'(\d{4}\.\d{2}\.\d{2})(?:p([1-9]\d*))?', version)
    if not match or int(match[2] or 0) > 65535:
        raise ValueError('Expected yyyy.MM.dd or yyyy.MM.ddpN')
    datetime.datetime.strptime(match[1], '%Y.%m.%d')
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    version = validate_version(args.version)
    manifest, entries = original_entries(args.source / 'resources/original')
    # A normal build cannot accidentally rewrite the old player's contract.
    for item, (key, raw) in zip(manifest['resources'], entries):
        if sha256(raw) != item['original_sha256'] or len(raw) != item['original_size']:
            raise ValueError(f'Original baseline changed: {key}; add a separate extension instead')
    if len(entries) != 192:
        raise ValueError('Expected all 192 original resources')
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'original.res').write_bytes(res_file(entries))
    metadata = dict(schema=1, extension_abi=1, version=version,
                    baseline_sha256=manifest['baseline_sha256'], original_resources=192,
                    repository='https://github.com/TTPlayerRebuild/TTPlayerRes')
    save_json(args.output / 'build.json', metadata)
    (args.output / 'abi.bin').write_bytes(b'TTPRES1\0' + struct.pack('<II', 1, 1))
    (args.output / 'metadata.rc').write_text(
        'LANGUAGE 4, 2\nTTPLAYER_RES_ABI 10 "abi.bin"\n'
        'TTPLAYER_RES_BUILD 10 "build.json"\n', encoding='utf-8')
    print(f'Compiled 192 immutable 5.7.9 resources; extension version {version}')


if __name__ == '__main__':
    main()
