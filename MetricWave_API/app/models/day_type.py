from app import db


class DayType(db.Model):
    __tablename__ = 'day_type'

    id = db.Column(db.Integer, primary_key=True)
    day_type = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<DayType(id={self.id}, day_type={self.day_type})>"
