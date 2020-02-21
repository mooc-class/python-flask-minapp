# -*- coding: utf-8 -*-
from web.controllers.api import route_api
from flask import request, jsonify,g
from common.models.food.Food import Food
from application import app,db
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from common.libs.UrlManager import UrlManager
from common.libs.Helper import selectFilterObj,getDictFilterField,getCurrentDate
from common.models.member.MemberComments import MemberComments
import json,datetime

@route_api.route("/my/order")
def myOrderList():
	resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
	member_info = g.member_info
	req = request.values
	status = int( req['status'] ) if 'status' in req else 0
	query = PayOrder.query.filter_by( member_id = member_info.id )
	if status == -8 :#等待付款
		query = query.filter( PayOrder.status == -8 )
	elif status == -7:#待发货
		query = query.filter( PayOrder.status == 1,PayOrder.express_status == -7,PayOrder.comment_status == 0 )
	elif status == -6:#待确认
		query = query.filter(PayOrder.status == 1, PayOrder.express_status == -6,PayOrder.comment_status == 0)
	elif status == -5:#待评价
		query = query.filter(PayOrder.status == 1, PayOrder.express_status == 1,PayOrder.comment_status == 0)
	elif status == 1:#已完成
		query = query.filter(PayOrder.status == 1, PayOrder.express_status == 1,PayOrder.comment_status == 1 )
	else:
		query = query.filter( PayOrder.status == 0 )

	pay_order_list = query.order_by( PayOrder.id.desc() ).all()
	data_pay_order_list = []
	if pay_order_list:
		pay_order_ids = selectFilterObj( pay_order_list,"id" )
		pay_order_item_list = PayOrderItem.query.filter( PayOrderItem.pay_order_id.in_( pay_order_ids ) ).all()
		food_ids = selectFilterObj( pay_order_item_list,"food_id" )
		food_map = getDictFilterField( Food,Food.id,"id",food_ids )
		pay_order_item_map = {}
		if pay_order_item_list:
			for item in pay_order_item_list:
				if item.pay_order_id not in pay_order_item_map:
					pay_order_item_map[ item.pay_order_id ] = []

				tmp_food_info = food_map[ item.food_id ]
				pay_order_item_map[item.pay_order_id].append({
					'id':item.id,
					'food_id':item.food_id,
					'quantity':item.quantity,
					'price':str( item.price ),
					'pic_url':UrlManager.buildImageUrl( tmp_food_info.main_image ),
					'name':tmp_food_info.name
				})


		for item in pay_order_list:
			tmp_data = {
				'status':item.pay_status,
				'status_desc':item.status_desc,
				'date':item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
				'order_number':item.order_number,
				'order_sn':item.order_sn,
				'note':item.note,
				'total_price':str( item.total_price ),
				'goods_list':pay_order_item_map[ item.id ]
			}

			data_pay_order_list.append( tmp_data )
	resp['data']['pay_order_list'] = data_pay_order_list
	return jsonify(resp)

@route_api.route("/my/order/info")
def myOrderInfo():
	resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
	member_info = g.member_info
	req = request.values
	order_sn = req['order_sn'] if 'order_sn' in req else ''
	pay_order_info = PayOrder.query.filter_by( member_id=member_info.id ,order_sn = order_sn).first()
	if not pay_order_info:
		resp['code'] = -1
		resp['msg'] = "系统繁忙，请稍后再试~~"
		return jsonify(resp)

	express_info = {}
	if pay_order_info.express_info:
		express_info = json.loads( pay_order_info.express_info )

	tmp_deadline = pay_order_info.created_time + datetime.timedelta(minutes=30)
	info = {
		"order_sn":pay_order_info.order_sn,
		"status":pay_order_info.pay_status,
		"status_desc":pay_order_info.status_desc,
		"pay_price":str( pay_order_info.pay_price),
		"yun_price":str( pay_order_info.yun_price),
		"total_price":str( pay_order_info.total_price),
		"address":express_info,
		"goods": [],
		"deadline":tmp_deadline.strftime("%Y-%m-%d %H:%M")
	}

	pay_order_items = PayOrderItem.query.filter_by( pay_order_id = pay_order_info.id  ).all()
	if pay_order_items:
		food_ids = selectFilterObj( pay_order_items , "food_id")
		food_map = getDictFilterField(Food, Food.id, "id", food_ids)
		for item in pay_order_items:
			tmp_food_info = food_map[item.food_id]
			tmp_data = {
				"name": tmp_food_info.name,
				"price": str( item.price ),
				"unit": item.quantity,
				"pic_url": UrlManager.buildImageUrl( tmp_food_info.main_image ),
			}
			info['goods'].append( tmp_data )
	resp['data']['info'] = info
	return jsonify(resp)


@route_api.route("/my/comment/add",methods = [ "POST" ])
def myCommentAdd():
	resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
	member_info = g.member_info
	req = request.values
	order_sn = req['order_sn'] if 'order_sn' in req else ''
	score = req['score'] if 'score' in req else 10
	content = req['content'] if 'content' in req else ''

	pay_order_info = PayOrder.query.filter_by( member_id=member_info.id ,order_sn = order_sn).first()
	if not pay_order_info:
		resp['code'] = -1
		resp['msg'] = "系统繁忙，请稍后再试~~"
		return jsonify(resp)

	if pay_order_info.comment_status:
		resp['code'] = -1
		resp['msg'] = "已经评价过了~~"
		return jsonify(resp)

	pay_order_items = PayOrderItem.query.filter_by( pay_order_id = pay_order_info.id ).all()
	food_ids = selectFilterObj( pay_order_items,"food_id" )
	tmp_food_ids_str = '_'.join(str(s) for s in food_ids if s not in [None])
	model_comment = MemberComments()
	model_comment.food_ids = "_%s_"%tmp_food_ids_str
	model_comment.member_id = member_info.id
	model_comment.pay_order_id = pay_order_info.id
	model_comment.score = score
	model_comment.content = content
	db.session.add( model_comment )

	pay_order_info.comment_status = 1
	pay_order_info.updated_time = getCurrentDate()
	db.session.add( pay_order_info )

	db.session.commit()
	return jsonify(resp)

@route_api.route("/my/comment/list" )
def myCommentList():
	resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
	member_info = g.member_info
	comment_list = MemberComments.query.filter_by( member_id=member_info.id )\
		.order_by(MemberComments.id.desc()).all()
	data_comment_list = []
	if comment_list:
		pay_order_ids = selectFilterObj( comment_list,"pay_order_id" )
		pay_order_map = getDictFilterField( PayOrder,PayOrder.id,"id",pay_order_ids )
		for item in comment_list:
			tmp_pay_order_info = pay_order_map[ item.pay_order_id ]
			tmp_data = {
				"date":item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
				"content":item.content,
				"order_number":tmp_pay_order_info.order_number
			}
			data_comment_list.append( tmp_data )
	resp['data']['list'] = data_comment_list
	return jsonify(resp)



