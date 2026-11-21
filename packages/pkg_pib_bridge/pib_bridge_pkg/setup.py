from setuptools import find_packages, setup

package_name = 'pib_bridge'

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
    maintainer_email='noreply@example.com',
    description='Bridge between Georg and pib-backend',
    license='Apache-2.0',
    entry_points={'console_scripts': ['pib_bridge = pib_bridge.bridge_node:main']},
)
