import datetime

import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class WorkingHour(SqlAlchemyBase):
    __tablename__ = 'working_hours'

    working_hour_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    start_time = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    end_time = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    courier_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("couriers.courier_id"))

    courier = orm.relation("Courier")

    def create_time(self, hours):
        if hours:
            start = list(map(int, hours.split('-')[0].split(':')))
            end = list(map(int, hours.split('-')[1].split(':')))
            self.start_time = datetime.time(start[0], start[1])
            self.end_time = datetime.time(end[0], end[1])

    def get_str_time(self):
        return f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"