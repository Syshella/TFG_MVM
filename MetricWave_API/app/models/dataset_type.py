from app import db

class DatasetType(db.Model):
    __tablename__ = 'dataset_types'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(16), nullable=False)

    def __repr__(self):
        return f"<DatasetTypes(id={self.id}, type={self.type})>"
