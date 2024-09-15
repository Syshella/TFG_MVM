import requests
from flask import Flask, render_template, request, jsonify, make_response, Blueprint
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

result_blueprint = Blueprint('result', __name__)
API_URL = "http://127.0.0.1:9100/results"

@result_blueprint.route('/load_filters', methods=['GET'])
def load_filters():
    # Verifica si los datos están en las cookies
    afn_data = request.cookies.get('afnData')
    day_type_data = request.cookies.get('dayTypeData')
    model_type_data = request.cookies.get('modelTypeData')

    # Si los datos no están en cookies, haz la llamada a la API
    if not afn_data:
        afn_data = request.post(f'{API_URL}/dataset/afn)')
    # if not day_type_data:
    #     day_type_data = get_day_type_data()
    # if not model_type_data:
    #     model_type_data = get_model_type_data()

    # Renderiza la página con los datos
    response = make_response(render_template('results.html',
                                             afn_data=afn_data,
                                             day_type_data=day_type_data,
                                             model_type_data=model_type_data))

    # Guarda los datos en cookies por 1 día
    response.set_cookie('afnData', afn_data, max_age=60 * 60 * 24)
    response.set_cookie('dayTypeData', day_type_data, max_age=60 * 60 * 24)
    response.set_cookie('modelTypeData', model_type_data, max_age=60 * 60 * 24)

    return response


@result_blueprint.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        afn = request.form['afn']
        day_type = request.form['day_type']
        model_type = request.form['model_type']

        # Hacer la solicitud POST al backend
        try:
            response = requests.post(f'{API_URL}/search', json={'afn': afn, 'day_type': day_type, 'model': model_type})
            response_data = response.json()
            # print(response_data)

            barplot_image_url = f'http://127.0.0.1:9100/{response_data["barplot_image_url"]}'
            residual_scatterplot_image_url = f'http://127.0.0.1:9100/{response_data["residual_scatterplot_image_url"]}'
            scatterplot_image_url = f'http://127.0.0.1:9100/{response_data["scatterplot_image_url"]}'
            correlation_heatmap_image_url = f'http://127.0.0.1:9100/{response_data["correlation_heatmap_image_url"]}'
            global_errors = response_data['global_errors']
            print(global_errors)

            mape_error_value = [error['mape'] for error in global_errors if error['model_name']==model_type][0]

            if response.status_code == 200:
                return render_template('results.html', barplot_image_url=barplot_image_url,
                                       global_errors=global_errors, residual_scatterplot_image_url=residual_scatterplot_image_url,
                                       scatterplot_image_url=scatterplot_image_url, correlation_heatmap_image_url=correlation_heatmap_image_url,
                                       afn=afn, day_type=day_type, model_type=model_type, mape_error_value = mape_error_value)
            else:
                return jsonify({'error': 'An error occurred, please try again.'})
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f"An error occurred: {e}"})

