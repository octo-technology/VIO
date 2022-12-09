from setuptools import setup, find_packages

with open('../docs/supervisor.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read()

with open('requirements-dev.txt', 'r', encoding='utf-8') as f:
    requirements_dev = f.read()

setup(
    name='supervisor',
    version='0.1.0',
    author='ROLO, BASA, BAPO, KSA, YDR',
    author_email='rolo@octo.com',
    description='V.IO - Visual Inspection Orchestrator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/octo-technology/les-bg-de-la-data/s-s-all/tribu/tribu-augi/asset/vio_edge',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
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
            'supervisor = supervisor.__main__:main',
        ],
    },
)
