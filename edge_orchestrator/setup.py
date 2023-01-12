from setuptools import setup, find_packages

long_description = "The edge_orchestrator orchestrates the following steps as soon as it is triggered: " \
                   "image capture, image backup, metadata backup, model inference on images and saving results."

setup(
    name='edge_orchestrator',
    version='0.2.0',
    author='ROLO, BAPO, KSA, YDR',
    author_email='rolo@octo.com',
    description='vio-edge: orchestrator module',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/octo-technology/VIO',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache2.0',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(exclude=['tests*', 'data']),
    package_data={'edge_orchestrator': ['logger.cfg']},
    # data_files=[('config', ['config/inventory.json'])],
    install_requires=[
        'aiohttp==3.8.3',
        'azure-iot-device==2.12.0',
        'fastapi==0.60.0',
        'numpy==1.20.3',
        'Pillow==8.4.0',
        'pymongo==4.3.3',
        'uvicorn==0.20.0',
        'smart_open[azure]==5.2.0'
    ],
    extras_require={
        'dev': [
            'autopep8==1.5.7',
            'behave==1.2.6',
            'flake8==6.0.0',
            'freezegun==1.1.0',
            'pytest==6.2.4',
            'pytest-asyncio==0.15.1',
            'pytest-cov==2.12.0',
            'python-dotenv==0.21.0',
            'requests==2.26.0',
            'testcontainers==3.4.0'
        ]
    },
    python_requires='>=3.8.5',
    entry_points={
        'console_scripts': [
            'edge_orchestrator = edge_orchestrator.__main__:main',
        ],
    },
)
