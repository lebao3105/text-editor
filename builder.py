import argparse
import os
import glob
import shutil
import sys

from textworker import __version__

parser = argparse.ArgumentParser(
    description="Help setting up textworker easier",
    usage="'install' for install the project, 'build' to build, 'maketrans' to create translations (gettext required).\nThat's all."
)
parser.add_argument('--install-req', '-r', type=bool, help="Install requirements")
parser.add_argument('action', nargs='*')

opts = parser.parse_args()
if opts.install_req:
    os.system('{} -m pip install -r requirements.txt'.format(sys.executable))

def make_trans():
    msgfmt = shutil.which('msgfmt')
    gettext = shutil.which('xgettext')
    pywxrc = shutil.which('pywxrc')
    msgmerge = shutil.which('msgmerge')

    print('Going to use the following tools:')
    print('* xgettext : {}'.format(gettext))
    print('* msgmerge {}'.format(msgmerge))
    print('* msgfmt {}'.format(msgfmt))
    print('* pywxrc {} (that''s why you can''t make app translate without wxPython installed)'.format(pywxrc))
    print('#####################################')

    os.system(pywxrc + ' --gettext' + ' textworker/ui/preferences.xrc' + ' -o po/preferences.pot')
    os.system(pywxrc + ' --gettext' + ' textworker/ui/autosave.xrc' + ' -o po/autosave.pot')
    os.system(gettext \
              + ' --copyright-holder="Le Bao Nguyen <bao12345yocoo@gmail.com>"' \
              + ' --package-version={}'.format(__version__) \
              + ' -C --language=python' \
              + ' -f po/POTFILES'
              + ' -d textworker -o po/textworker.pot'
    )
    for line in open("po/LINGUAS", "r").read().split():
        target = 'po/{}.po'.format(line)
        os.system(msgmerge + ' {} po/textworker.pot'.format(target) + ' -o {}'.format(target))
        os.mkdir('po/{}'.format(line))
        os.mkdir('po/{}/LC_MESSAGES'.format(line))
        os.system(msgfmt + ' -D po ' + target.removeprefix('po/') + ' -o po/{}/LC_MESSAGES/{}.mo'.format(line, line))
    
    if os.path.isdir('textworker/po'):
        shutil.rmtree('textworker/po')
    shutil.copytree('po', 'textworker/po')

    print('#####################################')
    
def install():
    make_trans()
    return os.system('{} -m pip install .'.format(sys.executable))

def build():
    make_trans()
    os.system('{} -m pip install build wheel'.format(sys.executable))
    return os.system('{} -m build'.format(sys.executable))

def clean():
    try:
        # po directory
        dirs = glob.glob("po/*/LC_MESSAGES")
        for path in dirs:
            shutil.rmtree(path)
        for line in open("po/LINGUAS", "r").read().split():
            shutil.rmtree("po/{}".format(line))
        # textworker
        shutil.rmtree("textworker/po")
        # py build outputs
        for path in glob.glob("*.egg-info"):
            shutil.rmtree(path)
        shutil.rmtree("dist")
    except FileNotFoundError:
        pass

if 'maketrans' in opts.action:
    clean()
    make_trans()
elif 'build' in opts.action:
    clean()
    build()
elif 'install' in opts.action:
    clean()
    install()
elif 'clean' in opts.action:
    clean()