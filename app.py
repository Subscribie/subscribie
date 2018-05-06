# -*- coding: utf-8 -*-
"""
    hedgehog.app
    ~~~~~~~~~

    This module implements the central hedgehog application object.

    :copyright: (c) 2018 by Karma Crew
"""
class Hedgehog(Flask):
    """The Hedgehog object implements a flask application suited to subscription
    based web applications and acts as the central object. Once it is created 
    it will act as a central registry for default views, application workflow,
    the URL rules, and much more. Note most of the application must be defined
    in Jamla format, a yaml based application markup.

    Usually you create a :class:`Hedgehog` instance in your main module or
    in the :file:`__init__.py` file of your package like this::

        from hedgehog import Hedgehog
        app = Hedgehog(__name__)

    """
    def __init__(self, import_name):
        super(Hedgehog,self).__init__(import_name)
