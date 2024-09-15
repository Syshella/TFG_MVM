from sqlalchemy.orm import relationship

from app import db


class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))
    day_time = db.Column(db.DateTime)
    predicted_class_60 = db.Column(db.Float)
    model_name = db.Column(db.String(100))

    # Relación inversa con Dataset
    dataset = relationship("Dataset", back_populates="predictions")

    def __repr__(self):
        return f"<Prediction(id={self.id}, dataset_id={self.dataset_id}, model_name={self.model_name})>"
