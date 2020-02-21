# coding: utf-8
from sqlalchemy import Column, Date, DateTime, Index, Integer, Numeric
from sqlalchemy.schema import FetchedValue
from application import db


class StatDailyMember(db.Model):
    __tablename__ = 'stat_daily_member'
    __table_args__ = (
        db.Index('idx_date_member_id', 'date', 'member_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    member_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    total_shared_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    total_pay_money = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
