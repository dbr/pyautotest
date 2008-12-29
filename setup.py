from setuptools import setup
setup(
    name = "pyautotest",
    py_modules = ['pyautotest'],
    entry_points = {
        'console_scripts': [
            'pyautotest = pyautotest:main'
        ]
    }
)