from setuptools import find_packages, setup

package_name = 'command_gate'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='georg',
    maintainer_email='you@example.com',
    description='Forwards motor commands to the driver only in mode real',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'command_gate = command_gate.command_gate_node:main',
        ],
    },
)
