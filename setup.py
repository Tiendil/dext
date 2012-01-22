# coding: utf-8
import setuptools

setuptools.setup(
    name = 'DjangoNext',
    version = '0.1.0',
    author = 'Aleksey Yeletsky',
    author_email = 'a.eletsky@gmail.com',
    packages = setuptools.find_packages(),
    url = 'https://github.com/Tiendil/django-next',
    license = 'LICENSE',
    description = "minor extentions for django",
    long_description = open('README').read(),
    include_package_data = True # setuptools-git MUST be installed
)
