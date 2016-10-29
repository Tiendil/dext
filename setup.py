# coding: utf-8
import setuptools

setuptools.setup(
    name='Dext',
    version='0.3.0',
    description='minor extentions for django',
    long_description = open('README.rst').read(),
    url='https://github.com/Tiendil/dext',
    author='Aleksey Yeletsky <Tiendil>',
    author_email='a.eletsky@gmail.com',
    license='BSD',
    install_requires=[
        'Django==1.10.2',
        'argon2_cffi==16.2.0',
        'Jinja2>=2.6'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',

        'Topic :: Games/Entertainment',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',

        'Framework :: Django :: 1.9',

        'Natural Language :: English'],
    keywords=['django'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    test_suite = 'tests',
    )
