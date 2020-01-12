from setuptools import find_packages, setup

setup(
    name='queuemanager',
    version='0.1.0',
    url='https://github.com/BCN3D/Queue-Manager-Server',
    license='GPL-3.0',
    author='Marc Bermejo',
    maintainer='Marc Bermejo',
    maintainer_email='mbermejo@bcn3dtechnologies.com',
    description='This server manages one printing queue for the connected printer',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask>=1.0',
        'flask-sqlalchemy',
        'sqlalchemy',
        'marshmallow<3.0.0',
        'flask-socketio',
        'flask-cors',
        'flask-restplus',
        'flask-jwt-extended',
        'cryptography',
        'click',
        'werkzeug',
        'eventlet',
        'psycopg2',
        'redis',
        'parse',
        "urllib3"
    ]
)
