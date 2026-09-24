from setuptools import find_packages, setup

package_name = 'input_grasp_planning'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='athome',
    maintainer_email='schneleel91097@th-nuernberg.de',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'input_grasp_planning_node = input_grasp_planning.input_grasp_planning:main',
        ],
    },
)
