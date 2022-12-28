from setuptools import setup, find_packages

long_description = "The edge_orchestrator orchestrates the following steps as soon as it is triggered: " \
                   "image capture, image backup, metadata backup, model inference on images and saving results."

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read()

with open('requirements-dev.txt', 'r', encoding='utf-8') as f:
    requirements_dev = f.read()

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
    packages=find_packages(exclude=['test', 'test.*', 'data']),
    install_requires=requirements,
    extras_require={
        'dev': requirements_dev
    },
    python_requires='>=3.8.5',
    entry_points={
        'console_scripts': [
            'edge_orchestrator = edge_orchestrator.__main__:main',
        ],
    },
)
