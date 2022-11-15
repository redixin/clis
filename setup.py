from setuptools import setup, find_packages

setup(
    name="clis",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["aiohttp<3.7.4", "pyyaml"],
    entry_points={"console_scripts": ["clis = clis.cli:run"]}
)
