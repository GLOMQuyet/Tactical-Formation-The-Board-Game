# /// script
# requires-python = ">=3.10"
# dependencies = ["pygame==2.6.1", "pyinstaller>=6.10,<7", "pillow>=10"]
# ///
"""Build a ready-to-run copy of the game (no Python needed to play it).

Makes one file in dist/ that is shared as it is, not zipped:
TacticalFormation-Windows-<arch>.exe, TacticalFormation-macOS-<arch>.dmg (a
disk image holding the app) or TacticalFormation-Linux-<arch>. GitHub Actions
runs this for every version tag (.github/workflows/build.yml) and attaches the
files to the release. Run with: uv run tools/build_app.py
"""

import os
import platform
import shutil
import subprocess
import sys
import time

import PyInstaller.__main__

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = 'TacticalFormation'
SYSTEM = {'win32': 'Windows', 'darwin': 'macOS'}.get(sys.platform, 'Linux')


def make_dmg(app, target):
    """Put the app in a disk image, next to a link to Applications."""
    stage = os.path.join(os.path.dirname(app), 'dmg')
    shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(stage)
    shutil.move(app, stage)
    os.symlink('/Applications', os.path.join(stage, 'Applications'))
    # hdiutil now and then fails with "Resource busy", or stalls, on build machines.
    for attempt in range(3):
        try:
            if subprocess.run(['hdiutil', 'create', '-volname', 'Tactical Formation',
                               '-srcfolder', stage, '-format', 'UDZO', '-ov', target],
                              timeout=300).returncode == 0:
                return
        except subprocess.TimeoutExpired:
            pass
        time.sleep(10)
    raise SystemExit('hdiutil could not make the disk image')


def main():
    os.chdir(REPO)
    dist, work = os.path.join(REPO, 'dist'), os.path.join(REPO, 'build')
    built = os.path.join(work, 'app')       # PyInstaller's output; dist/ gets the file to share
    shutil.rmtree(dist, ignore_errors=True)
    args = [
        os.path.join(REPO, 'main.py'),
        '--name', NAME,
        '--windowed',                                   # no console window
        '--noconfirm', '--clean',
        '--distpath', built, '--workpath', work, '--specpath', work,
        f'--add-data={os.path.join(REPO, "assets")}{os.pathsep}assets',
        '--icon', os.path.join(REPO, 'assets', 'green_piece.png'),
    ]
    # A macOS app is a folder (bundle); elsewhere one file is easiest to share.
    args.append('--onedir' if SYSTEM == 'macOS' else '--onefile')
    PyInstaller.__main__.run(args)

    os.makedirs(dist)
    stem = os.path.join(dist, f'{NAME}-{SYSTEM}-{platform.machine().lower()}')
    if SYSTEM == 'macOS':
        target = stem + '.dmg'
        make_dmg(os.path.join(built, f'{NAME}.app'), target)
    else:
        suffix = '.exe' if SYSTEM == 'Windows' else ''
        target = stem + suffix
        shutil.move(os.path.join(built, NAME + suffix), target)
    print(f'built {target} ({os.path.getsize(target) // (1024 * 1024)} MB)')


if __name__ == '__main__':
    main()
