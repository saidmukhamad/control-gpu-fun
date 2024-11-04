from setuptools import setup

setup(
    name='gpu_fan_control',
    version='0.0.1',
    author='saidmukhamad',
    author_email='saidmukhamadq@gmail.com',
    description='A package to control GPU fan speed based on temperature. (Nvidia)',
    packages=['gpu_fan_control'],
    install_requires=[
        'nvitop',
    ],
    entry_points={
        'console_scripts': [
            'gpu-fan-control=gpu_fan_control.control:main',
        ],
    },
)
