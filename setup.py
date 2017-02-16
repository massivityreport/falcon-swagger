#!/usr/bin/env python

from setuptools import setup

import falcon_swagger

setup(name='falcon-swagger',
      version=falcon_swagger.__version__,
      packages=[
        'falcon_swagger'
      ]
      )
