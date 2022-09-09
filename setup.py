from setuptools import setup  # type: ignore
from setuptools import find_packages


setup(
    name='seiscomp_scripts',
    version='0.2.0',
    description='',
    author='Jonathan Gosset',
    author_email='jonathan.gosset@nrcan-rncan.gc.ca',
    packages=find_packages(),
    install_requires=[
        'click',
        'obspy'
    ],
    entry_points={
        'console_scripts': 
        [
            ('update_key_bindings=' +
             'seiscomp_scripts.bin.update_key_bindings:main'),
            'backfill_sds=seiscomp_scripts.bin.backfill_sds:main'
        ]
    }
)
