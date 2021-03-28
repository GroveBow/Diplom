import sqlalchemy
from sqlalchemy import orm

from utils import BASE_COMPLETE_TIME
from .db_session import SqlAlchemyBase




class OrderInProgress(SqlAlchemyBase):
    __tablename__ = 'orders_in_progress'
    order_in_progress_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.order_id"))
    courier_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("couriers.courier_id"))
    assign_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    complete_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    courier_type = sqlalchemy.Column(sqlalchemy.String)

    order = orm.relation("Order")
    courier = orm.relation("Courier")

    def set_duration(self, session):
        prev = session.query(OrderInProgress).filter(OrderInProgress.courier_id == self.courier_id,
                                                     OrderInProgress.complete_time != BASE_COMPLETE_TIME,
                                                     OrderInProgress.complete_time <= self.complete_time,
                                                     OrderInProgress.order_id != self.order_id).all()
        if prev:
            mx = max(prev, key=lambda s: s.complete_time)
            dif = self.complete_time - mx.complete_time
        else:
            dif = self.complete_time - self.assign_time
        self.duration = dif.seconds + dif.minutes * 60 + dif.hours * 3600 + dif.days * 3600 * 24
        print()

    def get_rating(self, session):
        average_times = []
        regions = [i.region for i in self.regions]
        for i in regions:
            length = len(session.query(OrderInProgress).filter(OrderInProgress.courier_id == self.courier_id,
                                                               OrderInProgress.complete_time != BASE_COMPLETE_TIME).all())
            average = 0
            next_time = 0
            for j in range(1, length + 1):
                complete_order = session.query(OrderInProgress).filter(OrderInProgress.courier_id == self.courier_id,
                                                                       OrderInProgress.complete_time != BASE_COMPLETE_TIME).all()[
                    j - 1]
                end = (complete_order.complete_time.hour * 60 + complete_order.complete_time.minute) * 60 + \
                      complete_order.complete_time.second
                if j == 1:
                    start = (complete_order.assign_time.hour * 60 + complete_order.assign_time.minute) * 60 + \
                            complete_order.assign_time.second
                    next_time = end
                else:
                    start = next_time
                    next_time = end
                diff = abs(end - start)
                average = ((j - 1) * average + diff) // j
            average_times.append(average)

        return (60 * 60 - min(min(average_times), 60 * 60)) / (60 * 60) * 5
