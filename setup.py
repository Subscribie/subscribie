import setuptools

setuptools.setup(
    name='subscribie',
    version="0.0.4",
    author="Karma Computing",
    author_email="subscribie@karmacomputing.co.uk",
    desciption="Recurring subscription management and billing",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'subscribiecli',
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
    ''',
)
