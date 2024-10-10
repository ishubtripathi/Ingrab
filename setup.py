from setuptools import setup, find_packages

setup(
    name='ingrab',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ingrab-downloader=ingrab.downloader:main',
        ],
    },
    install_requires=[
        'instaloader',  # This is needed to interact with Instagram
    ],
)
