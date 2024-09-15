import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
from flask import Blueprint, jsonify, request, send_from_directory
from flasgger import swag_from
from sklearn.preprocessing import MinMaxScaler
from app.models.dataset import Dataset
from app.models.metric import Metric
from app.models.prediction import Prediction
from app.models.dataset_row import DatasetRow
from app import db
import matplotlib.dates as mdates

# Define el blueprint como 'result'
result_blueprint = Blueprint('results', __name__)


@result_blueprint.route('/search', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'afn': {
                        'type': 'string',
                        'description': 'The AFN code',
                        'example': 'AFN01'
                    },
                    'day_type': {
                        'type': 'integer',
                        'description': 'The type of day',
                        'example': 1
                    },
                    'model': {
                        'type': 'string',
                        'description': 'The model name (optional, for filtering specific model)',
                        'example': 'Linear Regression'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'A simple message',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'description': 'A message describing the result'
                    }
                },
                'example': {
                    'message': 'Hello, this is a result endpoint for AFN: {afn}, Day Type: {day_type}, and Model: {model}!'
                }
            }
        },
        404: {
            'description': 'Invalid parameters'
        }
    }
})
def search():
    data = request.get_json()
    afn = data.get('afn')
    day_type = data.get('day_type')
    model = data.get('model')
    # print(afn, day_type, model)

    if not afn or not day_type or not model:
        return jsonify({"error": "Invalid parameters"}), 404

    dataset = db.session.query(Dataset).filter(Dataset.AFN == afn, Dataset.day_type == day_type).first()
    filename_barplot_model_errors = generate_bar_plot_error_metrics(dataset, afn, day_type, model)
    filename_scatter_plot = generate_scatter_plot_actual_vs_predicted(dataset, afn, day_type, model)
    filename_scatter_plot_residual = generate_residual_scatter_plot(dataset, afn, day_type, model)
    filename_correlation_hetmap = generate_radiation_heatmap(dataset, afn, day_type)
    # filename_correlation_hetmap = generate_correlation_heatmap(dataset, afn, day_type)
    global_errors = get_metrics_table(dataset.id)
    # generate_radiation_heatmap(dataset, afn, day_type)
    print(type(global_errors))

    # comment_images([filename_barplot_model_errors, filename_scatter_plot, filename_scatter_plot_residual,
    #                 filename_correlation_hetmap])
    return jsonify({
        "message": f"Image generated successfully! Bar Plot for model errors, Scatter Plot, Residual Scatter Plot and metrics table",
        "barplot_image_url": f"/results/static/{filename_barplot_model_errors}",
        "scatterplot_image_url": f"/results/static/{filename_scatter_plot}",
        "residual_scatterplot_image_url": f"/results/static/{filename_scatter_plot_residual}",
        "correlation_heatmap_image_url": f"/results/static/{filename_correlation_hetmap}",
        # "correlation_heatmap_image_url": f"/results/static/{filename_correlation_hetmap}",
        "global_errors": global_errors
    }), 200


def get_metrics_table(dataset_id):
    metrics = db.session.query(Metric).filter(Metric.dataset_id == dataset_id).all()

    if not metrics:
        return jsonify({'error': 'Metrics not found'}), 404

    # Prepara los datos para el JSON
    global_errors = []
    for metric in metrics:
        model_errors = {
            "model_name": metric.model_name,
            "mse": metric.mse,
            "rmse": metric.rmse,
            "mae": metric.mae,
            "mape": metric.mape,
            "r2": metric.r2
        }
        global_errors.append(model_errors)

    return global_errors


def generate_residual_scatter_plot(dataset, afn, day_type, model):
    window_size = 10
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404

    # Consigue los registros de predicciones y valores reales
    predictions = db.session.query(Prediction).filter(Prediction.dataset_id == dataset.id,
                                                      Prediction.model_name == model).all()
    actuals = db.session.query(DatasetRow).filter(DatasetRow.dataset_id == dataset.id).all()

    if not predictions or not actuals:
        return jsonify({'error': 'Data not found'}), 404

    # Prepara los datos para el gráfico
    data = {
        'Hora': [actual.class_day_time for actual in actuals],
        'Residual': [actual.class_60 - prediction.predicted_class_60 for actual, prediction in
                     zip(actuals, predictions)]
    }

    df = pd.DataFrame(data)

    # Añade una columna de suavización usando un promedio móvil
    df['Smooth Residual'] = df['Residual'].rolling(window=window_size).mean()

    # Configura el estilo y la paleta de Seaborn
    sns.set(style="white")

    # Asegura que el estilo de Seaborn se aplique al gráfico
    plt.figure(figsize=(12, 8))

    # Grafica los residuales con scatter plot
    sns.scatterplot(x='Hora', y='Residual', data=df, color=sns.color_palette("pastel")[2], label='Residual')

    # Grafica la línea de tendencia suavizada
    sns.lineplot(x='Hora', y='Smooth Residual', data=df, color='red', label='Smoothed Trend')

    plt.title(f'Residual Plot with Smoothed Trend for {model}', fontsize=16, fontweight='bold')
    plt.xlabel('Hora', fontsize=14)
    plt.ylabel('Residual (W/m²)', fontsize=14)

    # Formatear la hora en el eje x
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    plt.legend()

    # Crea la ruta para guardar la gráfica
    static_dir = os.path.join(os.getcwd(), 'app', 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    filename = f'{afn}_{day_type}_{model}_residual_scatter_plot_with_smoothing.png'
    filepath = os.path.join(static_dir, filename)

    # Guarda la gráfica
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

    return filename


def generate_scatter_plot_actual_vs_predicted(dataset, afn, day_type, model):
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404

    # Consigue los registros de predicciones y valores reales
    predictions = db.session.query(Prediction).filter(Prediction.dataset_id == dataset.id,
                                                      Prediction.model_name == model).all()
    actuals = db.session.query(DatasetRow).filter(DatasetRow.dataset_id == dataset.id).all()

    if not predictions or not actuals:
        return jsonify({'error': 'Data not found'}), 404

    # Prepara los datos para el gráfico
    data = {
        'Hora': [actual.class_day_time for actual in actuals],
        'Actual': [actual.class_60 for actual in actuals],
        'Predicted': [prediction.predicted_class_60 for prediction in predictions]
    }

    df = pd.DataFrame(data)

    # Configura el estilo y la paleta de Seaborn
    sns.set(style="whitegrid")

    # Asegura que el estilo de Seaborn se aplique al gráfico
    plt.figure(figsize=(12, 8))

    # Grafica los valores reales en azul
    sns.lineplot(x='Hora', y='Actual', data=df, color='blue', label='Actual')

    # Grafica las predicciones en naranja
    sns.lineplot(x='Hora', y='Predicted', data=df, color='orange', label='Predicted')

    plt.title(f'Actual vs Predicted [{model}]', fontsize=16, fontweight='bold')
    plt.xlabel('Time', fontsize=14)
    plt.ylabel('W/m²', fontsize=14)  # Cambio realizado aquí

    # Formatear la hora en el eje x
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # Cambio realizado aquí

    # Crea la ruta para guardar la gráfica
    static_dir = os.path.join(os.getcwd(), 'app', 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    filename = f'{afn}_{day_type}_{model}_scatter_plot_actualvsprediction.png'
    filepath = os.path.join(static_dir, filename)

    # Guarda la gráfica
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

    return filename


def generate_bar_plot_error_metrics(dataset, afn, day_type, highlight_model):
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404

    # Retrieve the metrics records
    metrics = db.session.query(Metric).filter(Metric.dataset_id == dataset.id).all()

    if not metrics:
        return jsonify({'error': 'Metrics not found'}), 404

    # Prepare data for the plot
    data = {
        'Modelos': [metric.model_name for metric in metrics],
        'MAPE': [metric.mape for metric in metrics],
    }

    df = pd.DataFrame(data)

    # Apply logarithmic normalization
    df['MAPE'] = df['MAPE'].apply(np.log1p)

    # Generate color palette, highlighting the selected model
    colors = ['lightgray' if model != highlight_model else 'orange' for model in df['Modelos']]

    # Set up the style and palette for Seaborn
    sns.set(style="whitegrid")

    # Ensure Seaborn's style is applied to the plot
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(x='Modelos', y='MAPE', data=df, palette=colors)

    # Add the MAPE values on top of each bar
    for index, value in enumerate(df['MAPE']):
        ax.text(index, value, f'{np.expm1(value):.1f}', color='black', ha="center", va="bottom", fontsize=12)

    plt.title(f'MAPE for Models', fontsize=16, fontweight='bold')
    plt.xlabel('Models', fontsize=14)
    plt.ylabel('MAPE(%)', fontsize=14)
    plt.xticks(rotation=45)

    # Create the path to save the plot
    static_dir = os.path.join(os.getcwd(), 'app', 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    filename = f'{afn}_{day_type}_bar_plot_mape.png'
    filepath = os.path.join(static_dir, filename)

    # Save the plot
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

    return filename

def generate_radiation_heatmap(dataset, afn, day_type):

    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404

    # Fetch the metrics for the dataset
    metrics = db.session.query(Metric).filter(Metric.dataset_id == dataset.id).all()

    if not metrics:
        return jsonify({'error': 'Metrics not found'}), 404

    # Prepare the data for the heatmap
    data = {
        'Model': [metric.model_name for metric in metrics],
        'MSE': [metric.mse for metric in metrics],
        'RMSE': [metric.rmse for metric in metrics],
        'MAE': [metric.mae for metric in metrics],
        'MAPE': [metric.mape for metric in metrics],
        # 'R2': [metric.r2 for metric in metrics]
    }
    # Convertir los datos en un DataFrame
    df = pd.DataFrame(data)

    # Configurar el índice en el nombre del modelo
    df.set_index('Model', inplace=True)

    # Normalizar las métricas (excepto R2, porque R2 puede tener valores negativos)
    scaler = MinMaxScaler()
    df[['MSE', 'RMSE', 'MAE', 'MAPE']] = scaler.fit_transform(df[['MSE', 'RMSE', 'MAE', 'MAPE']])

    # Crear el heatmap con las métricas
    plt.figure(figsize=(10, 6))
    ax = sns.heatmap(df, annot=True, cmap='coolwarm', cbar=True)
    plt.title('Comparison of Error Metrics Across Models')
    # Adjust the plot to make sure the y-axis labels are not cut off
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, ha="right", fontsize=12)
    plt.subplots_adjust(left=0.25)
    # Save the heatmap
    static_dir = os.path.join(os.getcwd(), 'app', 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    filename = f'{afn}_{day_type}_radiation_heatmap.png'
    filepath = os.path.join(static_dir, filename)
    plt.savefig(filepath)
    plt.close()
    return filename


def generate_correlation_heatmap(dataset, afn, day_type):
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404

    # Fetch the metrics for the dataset
    metrics = db.session.query(Metric).filter(Metric.dataset_id == dataset.id).all()

    if not metrics:
        return jsonify({'error': 'Metrics not found'}), 404

    # Prepare the data for the heatmap
    data = {
        'Model': [metric.model_name for metric in metrics],
        'MSE': [metric.mse for metric in metrics],
        'RMSE': [metric.rmse for metric in metrics],
        'MAE': [metric.mae for metric in metrics],
        'MAPE': [metric.mape for metric in metrics],
        'R2': [metric.r2 for metric in metrics]
    }

    df = pd.DataFrame(data)

    # Remove the 'Model' column, since it contains strings and can't be used in correlation
    df_numeric = df.drop(columns=['Model'])

    # Calculate the correlation matrix
    corr_matrix = df_numeric.corr()

    # Configure Seaborn style
    sns.set(style="white")

    # Create the heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)

    plt.title(f'Correlation Heatmap of Error Metrics', fontsize=16, fontweight='bold')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)

    # Save the heatmap
    static_dir = os.path.join(os.getcwd(), 'app', 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    filename = f'{afn}_{day_type}_correlation_heatmap.png'
    filepath = os.path.join(static_dir, filename)

    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

    return filename


@result_blueprint.route('/static/<path:filename>', methods=['GET'])
def serve_image(filename):
    static_dir = os.path.join(os.getcwd(), 'app', 'static')
    return send_from_directory(static_dir, filename)

#
# def comment_images(images):
#     openai.api_key = os.getenv("API_KEY")
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are an expert in data analysis."},
#             {"role": "user", "content": "Here are some images for analysis: "}
#         ]
#     )
#
#     print(response['choices'][0]['message']['content'])
#
#


