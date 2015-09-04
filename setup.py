from setuptools import setup, find_packages

setup(
    name='photoimport',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click'
    ],
    entry_points='''
        [console_scripts]
        photoimport=photoimport.cli:run
    ''',
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: System :: Archiving :: Backup",
        ],
)

