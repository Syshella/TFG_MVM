from .dataset_routes import dataset_blueprint
# from .dataset_row_routes import dataset_row_blueprint
from .day_type_routes import day_type_blueprint
from .results_routes import result_blueprint
from .user_routes import user_blueprint
from .prediction_routes import prediction_blueprint

def register_routes(app):
    app.register_blueprint(dataset_blueprint, url_prefix='/datasets')
    # app.register_blueprint(dataset_row_blueprint, url_prefix='/dataset_rows')
    app.register_blueprint(user_blueprint, url_prefix='/users')
    app.register_blueprint(day_type_blueprint, url_prefix='/day_types')
    app.register_blueprint(prediction_blueprint, url_prefix='/predictions')
    app.register_blueprint(result_blueprint, url_prefix='/results')