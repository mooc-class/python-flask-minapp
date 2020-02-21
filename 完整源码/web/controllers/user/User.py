# -*- coding: utf-8 -*-
from flask import Blueprint,request,jsonify,make_response,g,redirect
from common.models.User import ( User )
from common.libs.user.UserService import ( UserService )
from common.libs.Helper import ( ops_render )
from common.libs.UrlManager import ( UrlManager )
from application import app,db
import json

route_user = Blueprint( 'user_page',__name__ )

@route_user.route( "/login",methods = [ "GET","POST" ] )
def login():
    if request.method == "GET":
        if g.current_user:
            return  redirect( UrlManager.buildUrl("/") )
        return ops_render( "user/login.html" )

    resp = {'code': 200, 'msg': '登录成功~~', 'data': {}}
    req = request.values
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

    if  login_name is None or len( login_name ) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入正确的登录用户名~~"
        return jsonify( resp )

    if  login_pwd is None or len( login_pwd ) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入正确的邮箱密码~~"
        return jsonify(resp)

    user_info = User.query.filter_by( login_name = login_name ).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "请输入正确的登录用户名和密码-1~~"
        return jsonify(resp)

    if user_info.login_pwd != UserService.genePwd( login_pwd,user_info.login_salt ):
        resp['code'] = -1
        resp['msg'] = "请输入正确的登录用户名和密码-2~~"
        return jsonify(resp)

    if user_info.status != 1:
        resp['code'] = -1
        resp['msg'] = "账号已被禁用，请联系管理员处理~~"
        return jsonify(resp)

    response = make_response(json.dumps({'code': 200, 'msg': '登录成功~~'}))
    response.set_cookie( app.config['AUTH_COOKIE_NAME'], '%s#%s' % (
        UserService.geneAuthCode(user_info), user_info.uid),  60 * 60 * 24 * 120)  # 保存120天
    return response

@route_user.route( "/edit",methods = [ "GET","POST" ] )
def edit():
    if request.method == "GET":
        return ops_render( "user/edit.html",{ 'current':'edit' } )

    resp = { 'code':200,'msg':'操作成功~','data':{} }
    req = request.values
    nickname = req['nickname'] if 'nickname' in req else ''
    email = req['email'] if 'email' in req else ''

    if nickname is None or len( nickname ) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的姓名~~"
        return jsonify( resp )

    if email is None or len( email ) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的邮箱~~"
        return jsonify( resp )

    user_info = g.current_user
    user_info.nickname = nickname
    user_info.email = email

    db.session.add( user_info )
    db.session.commit()
    return jsonify(resp)


@route_user.route( "/reset-pwd",methods = [ "GET","POST" ] )
def resetPwd():
    if request.method == "GET":
        return ops_render( "user/reset_pwd.html",{ 'current':'reset-pwd' } )

    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values

    old_password = req['old_password'] if 'old_password' in req else ''
    new_password = req['new_password'] if 'new_password' in req else ''

    if old_password is None or len( old_password ) < 6:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的原密码~~"
        return jsonify(resp)

    if new_password is None or len( new_password ) < 6:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的新密码~~"
        return jsonify(resp)

    if old_password == new_password:
        resp['code'] = -1
        resp['msg'] = "请重新输入一个吧，新密码和原密码不能相同哦~~"
        return jsonify(resp)

    user_info = g.current_user
    
    if user_info.login_pwd != UserService.genePwd( old_password,user_info.login_salt ):
        resp['code'] = -1
        resp['msg'] = "原密码不对~~"
        return jsonify(resp)

    if user_info.uid == 1:
        resp['code'] = -1
        resp['msg'] = "该用户是演示账号，不准修改密码和登录用户名~~"
        return jsonify(resp)

    user_info.login_pwd = UserService.genePwd( new_password,user_info.login_salt )

    db.session.add( user_info )
    db.session.commit()

    response = make_response(json.dumps( resp ))
    response.set_cookie(app.config['AUTH_COOKIE_NAME'], '%s#%s' % (
        UserService.geneAuthCode(user_info), user_info.uid), 60 * 60 * 24 * 120)  # 保存120天
    return response


@route_user.route( "/logout" )
def logout():
    response = make_response(redirect(UrlManager.buildUrl("/user/login")))
    response.delete_cookie(app.config['AUTH_COOKIE_NAME'])
    return response