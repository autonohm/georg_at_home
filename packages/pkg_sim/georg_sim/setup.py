from setuptools import find_packages, setup

package_name = 'georg_sim'

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
    description='2D simulator of Georg: cmd_vel in, odom/scan/tf out',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'sim2d = georg_sim.sim2d_node:main',
            'simmj = georg_sim.simmj_node:main',
            'sim_camera = georg_sim.camera_node:main',
        ],
    },
)
