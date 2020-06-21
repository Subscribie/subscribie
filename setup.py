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
        'flask_uploads @ git+https://github.com/maxcountryman/flask-uploads/@f66d7dc93e684fa0a3a4350a38e41ae00483a796#egg=Flask-Uploads-0.2.2.dev@41b95ec#egg=package-two',
        'flask_wtf',
        'wtforms[email]',
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
