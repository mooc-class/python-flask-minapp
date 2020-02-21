# -*- coding: utf-8 -*-
from flask import Blueprint,request,jsonify
from application import  app
import re,json
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager
from common.models.Image import Image
route_upload = Blueprint('upload_page', __name__)

'''
参考文章：https://segmentfault.com/a/1190000002429055
'''

@route_upload.route("/ueditor",methods = [ "GET","POST" ])
def ueditor():

	req = request.values
	action = req['action'] if 'action' in req else ''

	if action == "config":
		root_path = app.root_path
		config_path = "{0}/web/static/plugins/ueditor/upload_config.json".format( root_path )
		with open( config_path,encoding="utf-8" ) as fp:
			try:
				config_data =  json.loads( re.sub( r'\/\*.*\*/' ,'',fp.read() ) )
			except:
				config_data = {}
		return  jsonify( config_data )

	if action == "uploadimage":
		return uploadImage()

	if action == "listimage":
		return listImage()

	return "upload"

@route_upload.route("/pic",methods = [ "GET","POST" ])
def uploadPic():
	file_target = request.files
	upfile = file_target['pic'] if 'pic' in file_target else None
	callback_target = 'window.parent.upload'
	if upfile is None:
		return "<script type='text/javascript'>{0}.error('{1}')</script>".format( callback_target,"上传失败" )

	ret = UploadService.uploadByFile(upfile)
	if ret['code'] != 200:
		return "<script type='text/javascript'>{0}.error('{1}')</script>".format(callback_target, "上传失败：" + ret['msg'])

	return "<script type='text/javascript'>{0}.success('{1}')</script>".format(callback_target,ret['data']['file_key'] )

def uploadImage():
	resp = { 'state':'SUCCESS','url':'','title':'','original':'' }
	file_target = request.files
	upfile = file_target['upfile'] if 'upfile' in file_target else None
	if upfile is None:
		resp['state'] = "上传失败"
		return jsonify(resp)

	ret = UploadService.uploadByFile( upfile )
	if ret['code'] != 200:
		resp['state'] = "上传失败：" + ret['msg']
		return jsonify(resp)

	resp['url'] = UrlManager.buildImageUrl( ret['data']['file_key'] )
	return jsonify( resp )

def listImage():
	resp = { 'state':'SUCCESS','list':[],'start':0 ,'total':0 }

	req = request.values

	start = int( req['start']) if 'start' in req else 0
	page_size = int( req['size']) if 'size' in req else 20

	query = Image.query
	if start > 0:
		query = query.filter( Image.id < start )

	list = query.order_by( Image.id.desc() ).limit( page_size ).all()
	images = []

	if list:
		for item in list:
			images.append( { 'url': UrlManager.buildImageUrl( item.file_key ) } )
			start = item.id
	resp['list'] = images
	resp['start'] = start
	resp['total'] = len( images )
	return jsonify( resp )

