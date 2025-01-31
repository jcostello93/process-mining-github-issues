from setuptools import setup, find_packages

setup(
    name='my_project',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'boto3>=1.36.2,<2.0',
        'requests>=2.32.3,<3.0',
        'pm4py==2.7.13.1',
    ],
)
