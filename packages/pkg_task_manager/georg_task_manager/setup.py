from setuptools import find_packages, setup

package_name = 'georg_task_manager'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    package_data={'georg_task_manager': ['catalog.yaml', 'mocks/scenarios/*.yaml']},
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'georg_task_manager/catalog.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='giu',
    maintainer_email='giu@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            # long-running node with services (P2)
            'task_manager = georg_task_manager.ros_bridge:main',
            # old variant: picks a mission from MISSION_ID / menu, runs it once, exits
            'task_manager_cli = georg_task_manager.main:main',
            'mock_packages = georg_task_manager.mocks.mock_packages:main',
        ],
    },
)
