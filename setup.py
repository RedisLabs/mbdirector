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
        'jsonschema==4.17.3',
        'click==8.1.3',
        'redis==4.5.5',
        'Flask==2.3.2'
    ],
    entry_points='''
        [console_scripts]
        mbdirector=mbdirector.main:cli
    '''
)
