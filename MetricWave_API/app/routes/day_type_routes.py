from flask import Blueprint, jsonify
from app.models.dataset import Dataset
from app.models.dataset_training_test import DatasetsTrainingTest
from app.models.day_type import DayType
from app import db
from flasgger.utils import swag_from


day_type_blueprint = Blueprint('day_type', __name__)


@day_type_blueprint.route('/', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Lista de Day Types asociados con datasets y datasets_training_test',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'El ID del Day Type'
                        },
                        'day_type': {
                            'type': 'string',
                            'description': 'El valor del Day Type'
                        }
                    }
                }
            }
        }
    }
})
def get_day_types():
    # Consulta que usa RIGHT JOIN para obtener los valores de day_type
    day_types = db.session.query(DayType.id, DayType.day_type) \
        .join(Dataset, DayType.id == Dataset.day_type, isouter=False) \
        .join(DatasetsTrainingTest, Dataset.id == DatasetsTrainingTest.datasets_id, isouter=False) \
        .distinct() \
        .all()

    return jsonify([{'id': dt.id, 'day_type': dt.day_type} for dt in day_types])
