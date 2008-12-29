from setuptools import setup
setup(
    name = "pyautotest",
    version = "1.0",
    py_modules = ['pyautotest'],
    entry_points = {
        'console_scripts': [
            'pyautotest = pyautotest:main'
        ]
    }
)