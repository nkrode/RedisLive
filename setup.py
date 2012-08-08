from distutils.core import setup
import os


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
redis_live_dir = 'RedisLive'

for dirpath, dirnames, filenames in os.walk(redis_live_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    name='RedisLive',
    version='1',
    author='Nitin Kumar',
    author_email='kumarnitin@live.com',
    packages=packages,
    data_files=data_files,
    scripts=['bin/redis-live', 'bin/redis-monitor'],
    url='http://github.com/kumarnitin/RedisLive',
    license='LICENSE.txt',
    description='Visualize your redis instances, analyze query patterns and spikes.',
    long_description=open('README.rst').read(),
    install_requires=[
        "argparse==1.2.1",
        "python-dateutil==1.5",
        "redis",
        "tornado==2.1.1",
    ],
)
