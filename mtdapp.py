# -*- coding: utf-8 -*-
"""Create an application instance."""

import os
from app import create_app

config_class = os.getenv('FLASK_ENV')
app = create_app(config_class)

