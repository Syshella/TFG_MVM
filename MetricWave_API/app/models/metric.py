from sqlalchemy.orm import relationship

from app import db


class Metric(db.Model):
    __tablename__ = 'metrics'

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))
    model_name = db.Column(db.String(100))
    mse = db.Column(db.Float)
    rmse = db.Column(db.Float)
    mae = db.Column(db.Float)
    mape = db.Column(db.Float)
    r2 = db.Column(db.Float)

    # Relación inversa con Dataset
    dataset = relationship("Dataset", back_populates="metrics")

    def __repr__(self):
        return f"<Metric(id={self.id}, model_name={self.model_name}, mse={self.mse})>"
