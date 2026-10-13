"""Export the required resource contract and offline build auditor."""
import argparse
from pathlib import Path
from resource_model import save_json, sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    files = {
        'sdk/include/ttpres/resource_extensions.h': 'include/ttpres/resource_extensions.h',
        'sdk/include/ttpres/resource_ids.h': 'include/ttpres/resource_ids.h',
        'resources/original/manifest.json': 'baseline.json',
        'tools/resource_model.py': 'tools/resource_model.py',
        'tools/audit.py': 'tools/audit.py',
    }
    # Remove only the obsolete, previously generated executable backup.
    (args.output / 'resources/player.rc').unlink(missing_ok=True)
    hashes = {}
    for original, relative in files.items():
        target = args.output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = (source / original).read_bytes()
        if not target.exists() or target.read_bytes() != payload:
            target.write_bytes(payload)
        hashes[relative] = sha256(target.read_bytes())
    save_json(args.output / 'sdk.json', dict(schema=1, extension_abi=1,
              repository='https://github.com/TTPlayerRebuild/TTPlayerRes', files=hashes))


if __name__ == '__main__':
    main()
