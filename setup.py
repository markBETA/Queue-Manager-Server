from setuptools import find_packages, setup
setup(
    name='queuemanager',
    version='0.0.1',
    url='https://github.com/BCN3D/Queue-Manager-Server',
    license='GPL-3.0',
    author='Eloi Pardo',
    maintainer='Eloi Pardo',
    maintainer_email='epardo@fundaciocim.org',
    description='This server manages the users prints for a printer.',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask>=1.0',
        'flask-sqlalchemy',
        'marshmallow==2.15.6',
        'flask-marshmallow',
        'flask-socketio',
        'flask-cors',
        'flask-restplus',
        'sqlalchemy',
        'marshmallow-sqlalchemy',
        'click',
        'werkzeug',
        'eventlet',
        'requests',
        'flask-jwt-extended',
        'pymysql'
    ]
)


