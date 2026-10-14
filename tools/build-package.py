#!/usr/bin/env python3
"""Build and pack Concert Grand with RackForge's own validated packer."""
import argparse
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import tomllib


def main():
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rackforge-root', type=Path,
                        default=Path(os.environ.get('RACKFORGE_ROOT', root.parent / 'rackforge')))
    parser.add_argument('--component', type=Path, help='Use an already-built component')
    parser.add_argument('--native', action='append', default=[], metavar='PLATFORM=LIBRARY')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    version = tomllib.loads((root / 'plugin/package/rackforge-plugin.toml').read_text(encoding='utf-8'))['version']
    output = (args.output or root / f'artifacts/RF-Concert-Grand-{version}.rfplugin').resolve()
    if output.exists() or output.suffix != '.rfplugin':
        parser.error('output must be a new .rfplugin file')
    component = args.component
    if component is None:
        subprocess.run(['cargo', 'build', '--locked', '--release', '--target',
                        'wasm32-unknown-unknown', '-p', 'rackforge-concert-grand'], cwd=root, check=True)
        component = root / 'target/wasm32-unknown-unknown/release/rackforge_concert_grand.wasm'
    component = component.resolve(strict=True)
    host = args.rackforge_root.resolve(strict=True)
    executable = 'rackforge-store.exe' if os.name == 'nt' else 'rackforge-store'
    candidates = [host / 'bin' / executable, host / 'target/release' / executable]
    command = next(([str(p)] for p in candidates if p.is_file()), None)
    if command is None:
        command = ['cargo', 'run', '--locked', '--release', '--manifest-path',
                   str(host / 'Cargo.toml'), '-p', 'rackforge-store', '--']
    native = []
    for value in args.native:
        platform, separator, path = value.partition('=')
        if not separator or not platform:
            parser.error('--native requires PLATFORM=LIBRARY')
        native += ['--native', f'{platform}={Path(path).resolve(strict=True)}']
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='concert-grand-package-') as directory:
        stage = Path(directory) / 'package'
        shutil.copytree(root / 'plugin/package', stage)
        for name in ('LICENSE', 'NOTICE.md'):
            shutil.copyfile(root / name, stage / name)
        subprocess.run([*command, 'pack-wasm', str(stage), str(component), str(output), *native],
                       cwd=host, check=True)
    print(output)


if __name__ == '__main__':
    main()
