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
        "Django>=1.9",
        "Jinja2>=2.6",
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',

        'Topic :: Games/Entertainment',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',

        'Framework :: Django :: 1.9',

        'Natural Language :: English'],
    keywords=['django'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    test_suite = 'tests',
    )
