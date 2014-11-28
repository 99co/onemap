from distutils.core import setup

try:
  import pypandoc
  readme = pypandoc.convert("README.md", "rst")
except (IOError, ImportError):
  readme = open("README.md").read()

setup(
    name='onemap',
    version='0.2.0',
    author='Ruiwen Chua',
    author_email='ruiwen@99.co',
    packages=['onemap'],
    url='https://github.com/99co/onemap',
    license='LICENSE.txt',
    description='Wrapper for the OneMap API',
    long_description=readme,
    keywords=['onemap'],
    install_requires=[
        "requests >= 1.2.3"
    ]
)
