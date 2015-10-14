from setuptools import setup, find_packages

setup(
    name="cloud-init-server",
    version="0.0.1dev",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["aiohttp", "pyyaml"],
    entry_points={"console_scripts": ["cloud-init-server = initserver.cli:run"]}
)
