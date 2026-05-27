from setuptools import setup, find_packages

# Read README
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except:
    long_description = "Ingrab - Instagram Media Downloader"

setup(
    name='ingrab',
    version='1.4.0',
    packages=find_packages(),
    install_requires=[
        'instaloader>=4.8.3',
    ],
    author='Shubhrant Tripathi',
    author_email='ishubtripathi@gmail.com',
    description='A user-friendly application for downloading posts, reels, and profile pictures from public Instagram profiles.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ishubtripathi/Ingrab',
    project_urls={
        'Bug Reports': 'https://github.com/ishubtripathi/Ingrab/issues',
        'Source': 'https://github.com/ishubtripathi/Ingrab',
    },
    keywords=[
        # Core keywords
        'ingrab', 'instagram', 'insta', 'post', 'reel', 'downloader', 'cli', 'media', 'tools',
        
        # Instagram related
        'instagram-downloader', 'instagram-media-downloader', 'instagram-posts', 'instagram-reels',
        'instagram-stories', 'instagram-highlights', 'instagram-profile-picture', 'instagram-content',
        'ig-downloader', 'ig-posts', 'ig-reels', 'ig-stories', 'insta-downloader',
        
        # Download related
        'media-downloader', 'social-media-downloader', 'photo-downloader', 'video-downloader',
        'batch-downloader', 'bulk-downloader', 'image-downloader', 'content-downloader',
        
        # Features
        'rate-limiting', 'instagram-scraper', 'instagram-api-alternative', 'no-login',
        'instagram-saver', 'instagram-backup', 'instagram-archiver', 'instagram-grabber',
        
        # Technical
        'command-line-tool', 'python-cli', 'python-tool', 'automation-tool',
        'web-scraping', 'media-scraper', 'content-scraper',
        
        # Social media
        'social-media-tool', 'social-media-saver', 'content-saver', 'media-archiver',
        
        # Popular searches
        'save-instagram-posts', 'download-instagram-photos', 'backup-instagram',
        'instagram-photo-downloader', 'instagram-video-downloader', 'reels-downloader',
        
        # Additional
        'instaloader-alternative', 'instagram-tool', 'media-backup', 'photo-saver'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'ingrab=ingrab.downloader:main',
        ],
    },
)