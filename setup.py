
from setuptools import setup

setup(
    name =             "cui_gdb",
    version =          "0.0.1",
    author =           "Christoph Landgraf",
    author_email =     "christoph.landgraf@googlemail.com",
    description =      "GDB Frontend for cui",
    license =          "BSD",
    url =              "https://github.com/clandgraf/cui_gdb",
    packages =         ['cui_gdb'],
    install_requires = ['cui', 'cui_source']
)
