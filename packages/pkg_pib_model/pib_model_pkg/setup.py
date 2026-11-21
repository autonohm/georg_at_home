import glob
import os

from setuptools import find_packages, setup

package_name = 'pib_model'


def model_files():
    """Return the converted model files (generated at image build time into model/)."""
    out = []
    for path in glob.glob('model/**/*', recursive=True):
        if os.path.isfile(path):
            out.append((os.path.join('share', package_name, os.path.dirname(path)), [path]))
    return out


setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ] + model_files(),
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='georg',
    maintainer_email='noreply@example.com',
    description='Movable pib on Georg for Lichtblick',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pib_model_node = pib_model.model_node:main',
            'fake_pib_motors = pib_model.fake_motors:main',
            'convert_pib_model = pib_model.convert:main',
        ],
    },
)
