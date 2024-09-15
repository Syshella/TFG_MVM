from app import db
from sqlalchemy.orm import relationship


class Dataset(db.Model):
    __tablename__ = 'datasets'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(50), nullable=False)
    active = db.Column(db.Boolean, default=True)
    AFN = db.Column(db.String(50), nullable=False)
    day_type = db.Column(db.Integer, db.ForeignKey('day_type.id'), nullable=False)
    window_type = db.Column(db.String(16), nullable=True)

    # Relaciones con otras tablas
    rows = relationship("DatasetRow", back_populates="dataset")
    metrics = relationship("Metric", back_populates="dataset")
    predictions = relationship("Prediction", back_populates="dataset")

    def __repr__(self):
        return f"<Dataset(id={self.id}, filename={self.filename}, AFN={self.AFN})>"
