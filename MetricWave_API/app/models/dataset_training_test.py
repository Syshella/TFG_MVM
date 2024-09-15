from app import db


class DatasetsTrainingTest(db.Model):
    __tablename__ = 'datasets_training_test'

    id = db.Column(db.Integer, primary_key=True)
    dataset_type = db.Column(db.String(16), nullable=False)
    datasets_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)

    def __repr__(self):
        return f"<DatasetsTrainingTest(id={self.id}, dataset_type={self.dataset_type}, datasets_id={self.datasets_id})>"
