"""
Setup script for Hydrology Data Bot
"""

from setuptools import setup, find_packages
import os
import sys

# อ่านเวอร์ชันจากไฟล์
with open('src/__init__.py', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"\'')
            break
    else:
        version = '1.0.0'

# อ่าน README
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = 'Hydrology Data Bot - ดึงข้อมูลระดับน้ำจากกรมชลประทาน'

setup(
    name='hydrology-data-bot',
    version=version,
    author='Your Name',
    author_email='your.email@example.com',
    description='แอปพลิเคชันดึงข้อมูลระดับน้ำจากกรมชลประทาน (RID)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/hydrology-data-bot',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests>=2.31.0',
        'pandas>=2.0.0',
        'schedule>=1.2.0',
    ],
    entry_points={
        'console_scripts': [
            'hydrology-bot=src.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Topic :: Scientific/Engineering :: Hydrology',
        'Topic :: Utilities',
    ],
    python_requires='>=3.7',
    keywords='hydrology, water-level, thailand, rid, data-collection',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/hydrology-data-bot/issues',
        'Source': 'https://github.com/yourusername/hydrology-data-bot',
        'Documentation': 'https://github.com/yourusername/hydrology-data-bot/wiki',
    },
)
