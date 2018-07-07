import setuptools

setuptools.setup(
    name='Subscribie',
    version="0.0.1",
    author="Christopher Simpson",
    author_email="chris@karmacomputing.co.uk",
    desciption="Recurring subscription management and billing",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 2",
        "OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'Click',
        'flask',
        'flask_cors',
        'flask_login', 
        'flask_uploads',
        'flask_wtf',
        'requests',
        'blinker',
        'oauth2client',
        'pyyaml',
        'stripe',
        'gocardless_pro',
    ],
    entry_points='''
        [console_scripts]
        subscribie=subscribie:cli
    ''',
)
