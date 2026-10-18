# /// script
# requires-python = ">=3.10"
# dependencies = ["pygame==2.6.1", "pyinstaller>=6.10,<7", "pillow>=10"]
# ///
"""Build a ready-to-run copy of the game (no Python needed to play it).

Makes dist/TacticalFormation-<system>.zip holding a single program on Windows
and Linux, or an app bundle on macOS. GitHub Actions runs this for every
version tag (.github/workflows/build.yml) and attaches the zips to the
release. Run with: uv run tools/build_app.py
"""

import os
import platform
import shutil
import subprocess
import sys

import PyInstaller.__main__

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = 'TacticalFormation'
SYSTEM = {'win32': 'Windows', 'darwin': 'macOS'}.get(sys.platform, 'Linux')


def main():
    os.chdir(REPO)
    dist, work = os.path.join(REPO, 'dist'), os.path.join(REPO, 'build')
    shutil.rmtree(dist, ignore_errors=True)
    args = [
        os.path.join(REPO, 'main.py'),
        '--name', NAME,
        '--windowed',                                   # no console window
        '--noconfirm', '--clean',
        '--distpath', dist, '--workpath', work, '--specpath', work,
        f'--add-data={os.path.join(REPO, "assets")}{os.pathsep}assets',
        '--icon', os.path.join(REPO, 'assets', 'green_piece.png'),
    ]
    # A macOS app is a folder (bundle); elsewhere one file is easiest to share.
    args.append('--onedir' if SYSTEM == 'macOS' else '--onefile')
    PyInstaller.__main__.run(args)

    archive = os.path.join(dist, f'{NAME}-{SYSTEM}-{platform.machine().lower()}.zip')
    if SYSTEM == 'macOS':
        # ditto keeps the bundle's symlinks and signature intact.
        subprocess.run(['ditto', '-c', '-k', '--keepParent',
                        os.path.join(dist, f'{NAME}.app'), archive], check=True)
    else:
        program = NAME + ('.exe' if SYSTEM == 'Windows' else '')
        shutil.make_archive(archive[:-4], 'zip', dist, program)
    print(f'built {archive} ({os.path.getsize(archive) // (1024 * 1024)} MB)')


if __name__ == '__main__':
    main()
