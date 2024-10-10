from setuptools import setup, find_packages

version = {}
with open("version.py") as fp:
    exec(fp.read(), version)


setup(
    name='ingrab',
    version=version['__version__'],
    packages=find_packages(),
    install_requires=[
        'instaloader',
    ],
    author='Shubh Tripathi',
    author_email='bugingrab@gmail.com',
    description='A user-friendly application for downloading posts and reels from Instagram profiles.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ishubtripathi/Ingrab.git',
    keywords=['ingrab','InGrabe','instagram','insta','post','reel','downloader','cli'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'ingrab=ingrab.downloader:main', 
        ],
    },
)
