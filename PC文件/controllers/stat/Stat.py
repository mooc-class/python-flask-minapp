# -*- coding: utf-8 -*-
from flask import Blueprint,render_template

route_stat = Blueprint( 'stat_page',__name__ )

@route_stat.route( "/index" )
def index():
    return render_template( "stat/index.html" )

@route_stat.route( "/food" )
def food():
    return render_template( "stat/food.html" )

@route_stat.route( "/member" )
def memebr():
    return render_template( "stat/member.html" )

@route_stat.route( "/share" )
def share():
    return render_template( "stat/share.html" )
