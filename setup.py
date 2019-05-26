#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Install script for sunpower_pvs_exporter module
"""
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='sunpower_pvs_exporter',
      version='1.0',
      description='A Prometheus Exporter for the SunPower PVS Device',
      license='MIT',
      keywords="sunpower pvs prometheus exporter",
      long_description=read('README.md'),
      long_description_content_type='text/markdown',
      author='Gino Ledesma',
      author_email='gledesma@gmail.com',
      url='https://github.com/ginoledesma/sunpower-pvs-exporter/',
      packages=['sunpower_pvs_exporter'],
      python_requires=">=2.7",
      install_requires=[
          "prometheus_client",
          "requests",
      ],
      entry_points={
          "console_scripts": [
              'sunpower-pvs-exporter = sunpower_pvs_exporter.__main__:main'
          ],
      },
      test_requires=[
          "pytest",
      ],
      classifiers=[
          'Environment :: Console',
          'License :: OSI Approved :: MIT License',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
     )
