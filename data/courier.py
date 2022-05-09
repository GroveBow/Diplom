import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy import func

from utils import BASE_COMPLETE_TIME, diff_time
from .db_session import SqlAlchemyBase
from .order import Order
from .order_in_progress import OrderInProgress
from .region import Region
from .working_hour import WorkingHour


class Courier(SqlAlchemyBase):
    __tablename__ = 'couriers'

    courier_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    courier_type = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    courier_login = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)

    regions = orm.relation("Region", back_populates='courier')
    working_hours = orm.relation("WorkingHour", back_populates='courier')
    orders = orm.relation("OrderInProgress", back_populates='courier')

    def update_regions(self, regions, session):
        session.query(Region).filter(Region.courier_id == self.courier_id).delete()
        for i in regions:
            session.add(Region(region=i, courier_id=self.courier_id))
        session.commit()

    def update_working_hours(self, hours, session):
        session.query(WorkingHour).filter(WorkingHour.courier_id == self.courier_id).delete()
        for i in hours:
            hour = WorkingHour(courier_id=self.courier_id)
            hour.create_time(i)
            session.add(hour)
        session.commit()

    def get_earning(self, session):
        coeff = {'foot': 2, 'bike': 5, 'car': 9}
        earning = 0
        complete_orders = [i for i in self.orders if i.complete_time != BASE_COMPLETE_TIME]
        for order in complete_orders:
            earning = earning + 500 * coeff[order.courier.courier_type]
        return earning


    def get_rating(self, session):
        average_times = {}
        regions = [i.region for i in self.regions]
        last_time = 0
        for region in regions:
            average_times[f'{region}'] = (0, 0)
        length = len([j for j in self.orders if j.complete_time != BASE_COMPLETE_TIME])
        for i in range(1, length + 1):
            order = [order for order in self.orders if order.complete_time != BASE_COMPLETE_TIME][i - 1]
            if i == 1:
                start = order.assign_time
            else:
                start = last_time
            last_time = order.complete_time
            average = (average_times[f'{order.order.region}'][0] * average_times[f'{order.order.region}'][1] +
                       diff_time(start, last_time)) // (average_times[f'{order.order.region}'][0] + 1)
            average_times[f'{order.order.region}'] = (average_times[f'{order.order.region}'][0] + 1,
                                                      average)
        minimum = []
        for i in average_times.keys():
            minimum.append(average_times[i][1])
        minimum = min(minimum)
        return (60*60 - min(minimum, 60*60))/(60*60) * 5