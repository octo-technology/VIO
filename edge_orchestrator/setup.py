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
        'fastapi==0.80.0',
        'numpy==1.24.1',
        'Pillow==9.3.0',
        'psycopg2-binary==2.9.5',
        'pymongo==4.3.3',
        'uvicorn==0.20.0',
        'smart_open[azure]==6.3.0',
        'google-cloud-storage==2.2.1',
        'python-multipart==0.0.5'
    ],
    extras_require={
        'dev': [
            'alembic==1.9.2',
            'autopep8==2.0.1',
            'behave==1.2.6',
            'flake8==6.0.0',
            'freezegun==1.2.2',
            'pytest==7.2.1',
            'pytest-asyncio==0.20.3',
            'pytest-cov==4.0.0',
            'python-dotenv==0.21.1',
            'requests[security]==2.28.2',
            'testcontainers==3.7.1'
        ],
        'raspberry': [
            'picamera==1.13'
        ]
    },
    python_requires='>=3.8.5',
    entry_points={
        'console_scripts': [
            'edge_orchestrator = edge_orchestrator.__main__:main',
        ],
    },
)
