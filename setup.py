import os
import re
from distutils.command.build import build
from distutils.command.build_ext import build_ext
from setuptools.command.install import install
from distutils.spawn import find_executable
from distutils.version import LooseVersion
from setuptools import setup
from setuptools.extension import Extension
import subprocess

this_dir = os.path.dirname(os.path.abspath(__file__))

jamspell = Extension(
    name='_jamspell',
    include_dirs=['.', 'jamspell'],
    sources=[
        os.path.join('jamspell', 'lang_model.cpp'),
        os.path.join('jamspell', 'spell_corrector.cpp'),
        os.path.join('jamspell', 'utils.cpp'),
        os.path.join('jamspell', 'perfect_hash.cpp'),
        os.path.join('jamspell', 'bloom_filter.cpp'),
        os.path.join('contrib', 'cityhash', 'city.cc'),
        os.path.join('contrib', 'phf', 'phf.cc'),
        os.path.join('jamspell.i'),
    ],
    extra_compile_args=['-std=c++11', '-O2'],
    swig_opts=['-c++'],
)

class CustomBuild(build):
    def run(self):
        self.run_command('build_ext')
        build.run(self)


class CustomInstall(install):
    def run(self):
        self.run_command('build_ext')
        install.run(self)

class Swig3Ext(build_ext):
    def find_swig(self):
        swigBinary = find_executable('swig3.0') or find_executable('swig')
        assert swigBinary is not None
        assert subprocess.check_output([swigBinary, "-version"]).find(b'SWIG Version 3') != -1
        return swigBinary

VERSION = '0.0.12'

setup(
    name='jamspell-medSpellCheck',
    version=VERSION,
    author='Hank AI, Inc.',
    author_email='devs@hank.ai',
    url='https://github.com/hank-ai/medSpellCheck',
    download_url='https://github.com/hank-ai/medSpellCheck/tarball/' + VERSION,
    description='medical spell checker',
    long_description='context-based medical spell checker',
    keywords=['nlp', 'spell', 'spell-checker', 'jamspell', 'medical'],
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
    py_modules=['jamspell'],
    ext_modules=[jamspell],
    zip_safe=False,
    cmdclass={
        'build': CustomBuild,
        'install': CustomInstall,
        'build_ext': Swig3Ext,
    },
    include_package_data=True,
)
