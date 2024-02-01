from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in rise_pos_connector/__init__.py
from rise_pos_connector import __version__ as version

setup(
	name="rise_pos_connector",
	version=version,
	description="Rise POS Connector Custom App",
	author="Huda Infoteh",
	author_email="info@hudainfotech.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
