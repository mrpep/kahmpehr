from setuptools import setup

setup(
    name='kahmpehr',
    version='0.0.1',
    entry_points={
        'console_scripts': [
            'kahmpehr=run:main'
        ]
    }
)