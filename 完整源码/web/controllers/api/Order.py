# -*- coding: utf-8 -*-
from web.controllers.api import route_api
from flask import request, jsonify,g
from application import app, db
import json, decimal
from common.models.food.Food import Food
from common.models.pay.PayOrder import PayOrder
from common.libs.UrlManager import UrlManager
from common.libs.Helper import getCurrentDate
from common.libs.pay.PayService import PayService
from common.libs.pay.WeChatService import WeChatService
from common.libs.member.CartService import CartService
from common.models.member.MemberAddress import MemberAddress
from common.models.member.OauthMemberBind import OauthMemberBind


@route_api.route("/order/info", methods=[ "POST" ])
def orderInfo():
	resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
	req = request.values
	params_goods = req['goods'] if 'goods' in req else None
	member_info = g.member_info
	params_goods_list = []
	if params_goods:
		params_goods_list = json.loads(params_goods)

	food_dic = {}
	for item in params_goods_list:
		food_dic[item['id']] = item['number']

	food_ids = food_dic.keys()
	food_list = Food.query.filter(Food.id.in_(food_ids)).all()
	data_food_list = []
	yun_price = pay_price = decimal.Decimal(0.00)
	if food_list:
		for item in food_list:
			tmp_data = {
				"id": item.id,
				"name": item.name,
				"price": str(item.price),
				'pic_url': UrlManager.buildImageUrl(item.main_image),
				'number': food_dic[item.id]
			}
			pay_price = pay_price + item.price * int( food_dic[item.id] )
			data_food_list.append(tmp_data)

	# 获取地址
	address_info = MemberAddress.query.filter_by( is_default = 1,member_id = member_info.id,status = 1 ).first()
	default_address = ''
	if address_info:
		default_address = {
			"id": address_info.id,
			"name": address_info.nickname,
			"mobile": address_info.mobile,
			"address":"%s%s%s%s"%( address_info.province_str,address_info.city_str,address_info.area_str,address_info.address )
		}

	resp['data']['food_list'] = data_food_list
	resp['data']['pay_price'] = str(pay_price)
	resp['data']['yun_price'] = str(yun_price)
	resp['data']['total_price'] = str(pay_price + yun_price)
	resp['data']['default_address'] = default_address
	return jsonify(resp)

@route_api.route("/order/create", methods=[ "POST"])
def orderCreate():
	resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
	req = request.values
	type = req['type'] if 'type' in req else ''
	note = req['note'] if 'note' in req else ''
	express_address_id = int( req['express_address_id'] ) if 'express_address_id' in req and req['express_address_id'] else 0
	params_goods = req['goods'] if 'goods' in req else None

	items = []
	if params_goods:
		items = json.loads(params_goods)

	if len( items ) < 1:
		resp['code'] = -1
		resp['msg'] = "下单失败：没有选择商品~~"
		return jsonify(resp)

	address_info = MemberAddress.query.filter_by( id = express_address_id ).first()
	if not address_info or not address_info.status:
		resp['code'] = -1
		resp['msg'] = "下单失败：快递地址不对~~"
		return jsonify(resp)

	member_info = g.member_info
	target = PayService()
	params = {
		"note":note,
		'express_address_id':address_info.id,
		'express_info':{
			'mobile':address_info.mobile,
			'nickname':address_info.nickname,
			"address":"%s%s%s%s"%( address_info.province_str,address_info.city_str,address_info.area_str,address_info.address )
		}
	}
	resp = target.createOrder( member_info.id ,items ,params)
	#如果是来源购物车的，下单成功将下单的商品去掉
	if resp['code'] == 200 and type == "cart":
		CartService.deleteItem( member_info.id,items )

	return jsonify( resp )

@route_api.route("/order/pay", methods=[ "POST"])
def orderPay():
	resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
	member_info = g.member_info
	req = request.values
	order_sn = req['order_sn'] if 'order_sn' in req else ''
	pay_order_info = PayOrder.query.filter_by( order_sn = order_sn,member_id = member_info.id ).first()
	if not pay_order_info:
		resp['code'] = -1
		resp['msg'] = "系统繁忙。请稍后再试~~"
		return jsonify(resp)

	oauth_bind_info = OauthMemberBind.query.filter_by( member_id =  member_info.id ).first()
	if not oauth_bind_info:
		resp['code'] = -1
		resp['msg'] = "系统繁忙。请稍后再试~~"
		return jsonify(resp)

	config_mina = app.config['MINA_APP']
	notify_url = app.config['APP']['domain'] + config_mina['callback_url']

	target_wechat = WeChatService( merchant_key=config_mina['paykey'] )

	data = {
		'appid': config_mina['appid'],
		'mch_id': config_mina['mch_id'],
		'nonce_str': target_wechat.get_nonce_str(),
		'body': '订餐',  # 商品描述
		'out_trade_no': pay_order_info.order_sn,  # 商户订单号
		'total_fee': int( pay_order_info.total_price * 100 ),
		'notify_url': notify_url,
		'trade_type': "JSAPI",
		'openid': oauth_bind_info.openid
	}

	pay_info = target_wechat.get_pay_info( pay_data=data)

	#保存prepay_id为了后面发模板消息
	pay_order_info.prepay_id = pay_info['prepay_id']
	db.session.add( pay_order_info )
	db.session.commit()

	resp['data']['pay_info'] = pay_info
	return jsonify(resp)

@route_api.route("/order/callback", methods=[ "POST"])
def orderCallback():
	result_data = {
		'return_code': 'SUCCESS',
		'return_msg': 'OK'
	}
	header = {'Content-Type': 'application/xml'}
	config_mina = app.config['MINA_APP']
	target_wechat = WeChatService(merchant_key=config_mina['paykey'])
	callback_data = target_wechat.xml_to_dict( request.data )
	app.logger.info( callback_data  )
	sign = callback_data['sign']
	callback_data.pop( 'sign' )
	gene_sign = target_wechat.create_sign( callback_data )
	app.logger.info(gene_sign)
	if sign != gene_sign:
		result_data['return_code'] = result_data['return_msg'] = 'FAIL'
		return target_wechat.dict_to_xml(result_data), header
	if callback_data['result_code'] != 'SUCCESS':
		result_data['return_code'] = result_data['return_msg'] = 'FAIL'
		return target_wechat.dict_to_xml(result_data), header

	order_sn = callback_data['out_trade_no']
	pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
	if not pay_order_info:
		result_data['return_code'] = result_data['return_msg'] = 'FAIL'
		return target_wechat.dict_to_xml(result_data), header

	if int( pay_order_info.total_price * 100  ) != int( callback_data['total_fee'] ):
		result_data['return_code'] = result_data['return_msg'] = 'FAIL'
		return target_wechat.dict_to_xml(result_data), header

	if pay_order_info.status == 1:
		return target_wechat.dict_to_xml(result_data), header

	target_pay = PayService()
	target_pay.orderSuccess( pay_order_id = pay_order_info.id,params = { "pay_sn":callback_data['transaction_id'] } )
	target_pay.addPayCallbackData( pay_order_id = pay_order_info.id, data = request.data)
	return target_wechat.dict_to_xml(result_data), header

@route_api.route("/order/ops", methods=[ "POST"])
def orderOps():
	resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
	req = request.values
	member_info = g.member_info
	order_sn = req['order_sn'] if 'order_sn' in req else ''
	act = req['act'] if 'act' in req else ''
	pay_order_info = PayOrder.query.filter_by(order_sn=order_sn, member_id=member_info.id).first()
	if not pay_order_info:
		resp['code'] = -1
		resp['msg'] = "系统繁忙。请稍后再试~~"
		return jsonify(resp)


	if act == "cancel":
		target_pay = PayService( )
		ret = target_pay.closeOrder( pay_order_id=pay_order_info.id )
		if not ret:
			resp['code'] = -1
			resp['msg'] = "系统繁忙。请稍后再试~~"
			return jsonify(resp)
	elif act == "confirm":
		pay_order_info.express_status = 1
		pay_order_info.updated_time = getCurrentDate()
		db.session.add( pay_order_info )
		db.session.commit()

	return jsonify(resp)




