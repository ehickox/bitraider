from setuptools import setup, find_packages

setup(name='bitraider',
    version='0.0.4a0',
    description='A suite of tools for algorithmic Bitcoin trading',
    url='http://github.com/ehickox2012/bitraider',
    author='Eli Hickox',
    author_email='ehicko2@illinois.edu',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bitraider=bitraider.trader_template:run',
                ],
    },
    install_requires=[
        'numpy',
        'pytz',
        'datetime',
        'matplotlib',
    ],
    zip_safe=False)
