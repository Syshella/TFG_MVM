import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def generate_evaluation_metrics(date_afn):
    input_file = f'results/{date_afn}_testandscore.csv'
    df = pd.read_csv(input_file)
    # Skip the first two metadata rows
    df = df.iloc[2:]

    # Excluded columns from the dataset to get the model names used
    excluded_columns = ['Day_Type', 'AFN', 'Class_Datetime', 'Class_60', 'Fold', 'Feature_0', 'Feature_1', 'Feature_2',
                        'Feature_3', 'Feature_4', 'Feature_5', 'Feature_6', 'Feature_7', 'Feature_8', 'Feature_9',
                        'Feature_10', 'Feature_11', 'Feature_12', 'Feature_13', 'Feature_14', 'Feature_15',
                        'Feature_16', 'Feature_17', 'Feature_18', 'Feature_19', 'Feature_20', 'Feature_21',
                        'Feature_22', 'Feature_23', 'Feature_24', 'Feature_25', 'Feature_26', 'Feature_27',
                        'Feature_28', 'Feature_29', 'Feature_30', 'Feature_31', 'Feature_32', 'Feature_33',
                        'Feature_34', 'Feature_35', 'Feature_36', 'Feature_37', 'Feature_38', 'Feature_39',
                        'Feature_40', 'Feature_41', 'Feature_42', 'Feature_43', 'Feature_44', 'Feature_45',
                        'Feature_46', 'Feature_47', 'Feature_48', 'Feature_49', 'Feature_50', 'Feature_51',
                        'Feature_52', 'Feature_53', 'Feature_54', 'Feature_55', 'Feature_56', 'Feature_57',
                        'Feature_58', 'Feature_59']

    # List of models used in the dataset
    models = [col for col in df.columns if col not in excluded_columns]
    print(models)

    actual_values = df['Class_60'].apply(pd.to_numeric, errors='coerce')
    # Introduccion de la eliminacion de los valores = 0 para actual values
    df = df[actual_values != 0]
    actual_values = df['Class_60'].apply(pd.to_numeric, errors='coerce')
    # Initialize a dictionary to store the results
    results = {
        'Model': [],
        'MSE': [],
        'RMSE': [],
        'MAE': [],
        'MAPE': [],
        'R2': []
    }

    # Loop through each model's results
    for model in models:
        predictions = df[model].apply(pd.to_numeric, errors='coerce')

        mse = mean_squared_error(actual_values, predictions)
        rmse = np.sqrt(mse)
        # Misma unidad que la variable a predecir, no % como en el MAPE
        mae = mean_absolute_error(actual_values, predictions)
        # Added epsilon to avoid division by zero
        actual_values_epsilon = actual_values.replace(0, 1)
        mape = np.mean(np.abs((actual_values - predictions) / actual_values_epsilon)) * 100
        r2 = r2_score(actual_values, predictions)

        # Store the results
        results['Model'].append(model)
        results['MSE'].append(mse)
        results['RMSE'].append(rmse)
        results['MAE'].append(mae)
        results['MAPE'].append(mape)
        results['R2'].append(r2)

    # Convert the results to a DataFrame for easy viewing
    results_df = pd.DataFrame(results)

    # Display the results
    print(results_df)

    # # Save the results to a CSV file
    results_df.to_csv(f'results/{date_afn}_model_error_metrics.csv', index=False)


# STEP 1: Select the file to load the data
date_afn = "20150812_AFN11"
generate_evaluation_metrics(date_afn)


























