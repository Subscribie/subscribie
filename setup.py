import setuptools

setuptools.setup(
    name='subscribie',
    version="0.0.7",
    author="Karma Computing",
    author_email="subscribie@karmacomputing.co.uk",
    desciption="Recurring subscription management and billing",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'Flask>=1,<2',
        'flask_cors',
        'flask_login', 
        'flask_uploads',
        'flask_wtf',
        'Flask-Mail>=0.9.1',
        'requests',
        'blinker',
        'oauth2client',
        'pyyaml',
        'stripe',
        'gocardless_pro',
        'GitPython',
        'pytest',
        'tinycss',
        'flask_sqlalchemy',
        'flask_migrate',
        'python-dotenv==0.13.0'
    ],
    entry_points='''
        [console_scripts]
    ''',
)
