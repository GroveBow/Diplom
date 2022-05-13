import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from .delivery_hour import DeliveryHour


class Order(SqlAlchemyBase):
    __tablename__ = 'orders'
    order_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    weight = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    region = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    delivery_address = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    courier_taken = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    customer = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.login"))
    contactless_delivery = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    call_before_delivery = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    call_after_delivery = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    SMS_only = sqlalchemy.Column(sqlalchemy.Boolean, default=False)


    delivery_hours = orm.relation("DeliveryHour", back_populates='order')

    def update_delivery_hours(self, hours, session):
        session.query(DeliveryHour).filter(DeliveryHour.order_id == self.order_id).delete()
        for i in hours:
            hour = DeliveryHour(courier_id=self.courier_id)
            hour.set_delivery_hour(i)
            session.add(hour)
        session.commit()

    def get_status(self):
        return "В пути" if self.courier_taken else "Ждет отправки"
