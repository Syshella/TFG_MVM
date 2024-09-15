from flask import Blueprint, jsonify
from app.models.prediction import Prediction
from app import db
from flasgger.utils import swag_from

prediction_blueprint = Blueprint('prediction', __name__)


@prediction_blueprint.route('/model', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Lista de nombres únicos de modelos',
            'schema': {
                'type': 'array',
                'items': {
                        'type': 'string',
                        'description': 'El nombre del modelo',
                        'example': 'Linear Regression'
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
def get_model_names():
    model_names = db.session.query(Prediction.model_name).distinct().all()
    # return list of model names
    return jsonify([model.model_name for model in model_names])
