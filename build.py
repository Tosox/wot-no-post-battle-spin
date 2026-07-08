import argparse
import os
import shutil
import subprocess
import sys
import zipfile

MOD_ID = 'de.tosox.no_post_battle_spin'
VERSION = '1.0.0'
MOD_NAME = 'No Post-Battle Spin'
MOD_DESCRIPTION = 'Stops your tank from pivoting in place after the battle ends'

PYTHON27 = 'C:\\Python27\\python.exe'
GAME_DIR = 'C:\\Games\\World_of_Tanks_EU'
GAME_VERSION = '2.3.0.1'
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
BUILD = os.path.join(HERE, 'build')
PY_STAGE = os.path.join(BUILD, 'py_stage')
DIST = os.path.join(HERE, 'dist')
META_IN = os.path.join(HERE, 'meta.xml.in')

ENTRY_RES_DIR = 'scripts/client/gui/mods'
PKG_RES_DIR = 'scripts/client/no_post_battle_spin'
ENTRY_NAME = 'mod_no_post_battle_spin'
PKG_NAME = 'no_post_battle_spin'


def compile_pyc():
    if not os.path.exists(PYTHON27):
        sys.exit('Python 2.7 not found at %s - edit PYTHON27 in build.py' % PYTHON27)
    if os.path.exists(PY_STAGE):
        shutil.rmtree(PY_STAGE)
    shutil.copytree(SRC, PY_STAGE,
                    ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
    subprocess.check_call([PYTHON27, '-m', 'compileall', '-q', PY_STAGE])
    print('compiled -> %s' % PY_STAGE)


def iter_payload():
    entry = os.path.join(PY_STAGE, ENTRY_NAME + '.pyc')
    if not os.path.exists(entry):
        sys.exit('missing %s - compile step failed' % entry)
    yield entry, ENTRY_RES_DIR + '/' + ENTRY_NAME + '.pyc'

    pkg = os.path.join(PY_STAGE, PKG_NAME)
    for name in sorted(os.listdir(pkg)):
        if name.endswith('.pyc'):
            yield os.path.join(pkg, name), PKG_RES_DIR + '/' + name


def render_meta():
    with open(META_IN, 'r') as f:
        template = f.read()
    return template.format(id=MOD_ID, version=VERSION,
                           name=MOD_NAME, description=MOD_DESCRIPTION)


def build_wotmod():
    os.makedirs(DIST, exist_ok=True)
    out = os.path.join(DIST, '%s_%s.wotmod' % (MOD_ID, VERSION))
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_STORED) as z:
        z.writestr('meta.xml', render_meta())
        for src_path, res_rel in iter_payload():
            z.write(src_path, 'res/' + res_rel)
    print('packaged -> %s' % out)
    return out


def install_wotmod(wotmod_path):
    dst_dir = os.path.join(GAME_DIR, 'mods', GAME_VERSION)
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, os.path.basename(wotmod_path))
    shutil.copyfile(wotmod_path, dst)
    print('installed -> %s' % dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--install', action='store_true',
                    help="copy the built .wotmod into the game's mods/<version> folder")
    args = ap.parse_args()

    compile_pyc()
    wotmod = build_wotmod()
    if args.install:
        install_wotmod(wotmod)
    print('done.')


if __name__ == '__main__':
    main()
