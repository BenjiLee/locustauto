from setuptools import setup

setup(
    name='locustauto',
    version='0.1.0',
    author='Christopher Lee',
    author_email='christopherlee2012@gmail.com',
    py_modules=['locust_auto_test',],
    url='https://github.com/BenjiLee/locustauto',
    license='Apache2',
    description='Automatically Test with Locust.io',
    #long_description=open('README.rst').read(),
    install_requires=[
        'pyyaml==3.11',
        'locustio==0.7.2',
    ],
)
