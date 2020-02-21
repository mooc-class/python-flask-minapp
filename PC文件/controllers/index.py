# -*- coding: utf-8 -*-
from flask import Blueprint,render_template

route_index = Blueprint( 'index_page',__name__ )

@route_index.route("/")
def index():
    return render_template( "index/index.html" )