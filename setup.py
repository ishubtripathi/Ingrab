from setuptools import setup, find_packages

setup(
    name='ingrab',
    version='1.0.1',
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
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', 
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6', 
)
