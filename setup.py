from setuptools import setup
setup(
    name = "pyautotest",
    py_modules = ['pyautotest', 'rawr', 'netgrowl'],
    entry_points = {
        'console_scripts': [
            'pyautotest = pyautotest:main'
        ]
    }
)