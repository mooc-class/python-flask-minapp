# -*- coding: utf-8 -*-
from flask import Blueprint

route_index = Blueprint( 'index_page',__name__ )

@route_index.route("/")
def index():
    return "Hello World"