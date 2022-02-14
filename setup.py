from setuptools import setup, find_packages

setup(
    name='Lasagna',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pyqt5==5.15.6',
        'numpy',
        'tifffile',
        'pynrrd',
        'pyqtgraph',
        'pyyaml',
        'sip',
        'scikit-image',
        'scipy',
        'matplotlib',
    ],
    entry_points={
        "console_scripts": [
            'lasagna = lasagna.main:run',
        ]
    },
)
