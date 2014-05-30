from distutils.core import setup

setup(
    name='onemap',
    version='0.1',
    author='Ruiwen Chua',
    author_email='ruiwen@99.co',
    packages=['onemap'],
    url='http://pypi.python.org/pypi/TowelStuff/',
    license='LICENSE.txt',
    description='Wrapper for the OneMap API',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests >= 1.2.3"
    ],
)
