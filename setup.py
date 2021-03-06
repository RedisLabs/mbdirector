from setuptools import setup, find_packages
setup(
    name='mbdirector',
    version='0.1.0',
    url='https://github.com/RedisLabs/mbdirector',
    license='GPL',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    package_data={
        'mbdirector': ['schema/mbdirector_schema.json',
                       'static/css/*',
                       'templates/*']
    },
    install_requires=[
        'jsonschema==2.6.0',
        'click==7.0',
        'redis==3.5.3',
        'Flask==1.0.2'
    ],
    entry_points='''
        [console_scripts]
        mbdirector=mbdirector.main:cli
    '''
)
