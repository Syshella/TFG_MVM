from flask import Blueprint, jsonify
from app.models.dataset import Dataset
from app import db
from flasgger.utils import swag_from

dataset_blueprint = Blueprint('dataset', __name__)


@dataset_blueprint.route('/afn', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Lista de AFN únicos',
            'schema': {
                'type': 'array',
                'items': {
                        'type': 'string',
                        'description': 'AFN Number',
                        'example': 'AFN01'
                    }
            }
        },
        500: {
            'description': 'Error interno del servidor',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Internal server error'
                    }
                }
            }
        }
    }

})
def get_afn_names():
    afn_names = db.session.query(Dataset.AFN).distinct().all()
    # return list of AFN names
    return jsonify([model.AFN for model in afn_names])


