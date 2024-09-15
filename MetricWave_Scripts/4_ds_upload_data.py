from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Prediction, Metric
from database_connection import Config


def upload_predictions(input_file, dataset_id):
    """
    Inserts results from a CSV file into the database.

    Args:
        input_file (str): The path to the CSV file containing the results.
        dataset_id (int): The ID of the dataset to which the results belong.
    """
    # Create the engine using the Config class
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        df = pd.read_csv(input_file)
        # Exclude the first two metadata rows
        df = df[2:]
        # Retrieve the model names from the columns
        excluded_columns = ['Day_Type', 'AFN', 'Class_Datetime', 'Class_60', 'Fold', 'Feature_0', 'Feature_1',
                            'Feature_2',
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

        models = [col for col in df.columns if col not in excluded_columns]
        # print(models)
        predictions_data = []
        # Generates row for each model prediction
        for _, row in df.iterrows():
            for model in models:
                existing_prediction = session.query(Prediction).filter_by(dataset_id=dataset_id, day_time=row['Class_Datetime'], model_name=model).first()
                if existing_prediction:
                    # print(f" - Prediction for model {model} and day_time {row['Class_Datetime']} already exists in the database. Updating...")
                    existing_prediction.predicted_class_60 = float(row[model])
                else:
                    new_prediction = Prediction(
                        dataset_id = dataset_id,
                        day_time = datetime.strptime(row['Class_Datetime'], '%Y-%m-%d %H:%M:%S'),
                        predicted_class_60 = float(row[model]),
                        model_name = model
                    )
                    session.add(new_prediction)
        session.commit()
        print(f"Predictions for dataset {dataset_id} inserted successfully.")

    except Exception as e:
        session.rollback()  # Rollback in case of error
        print(f"Error: {e}")
    finally:
        session.close()  # Close the session


def upload_metrics(input_file, dataset_id):
    # Create the engine using the Config class
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        df = pd.read_csv(input_file)
        metrics = []
        for _, model in df.iterrows():
            existing_metric = session.query(Metric).filter_by(dataset_id=dataset_id,
                                                                     model_name=model['Model']).first()
            if existing_metric:
                # print(f" - Metrics for model {model['Model']} already exist in the database. Updating the existing values")
                existing_metric.mse = float(model['MSE'])
                existing_metric.rmse = float(model['RMSE'])
                existing_metric.mae = float(model['MAE'])
                existing_metric.mape = float(model['MAPE'])
                existing_metric.r2 = float(model['R2'])
            else:
                new_metric = Metric(
                    dataset_id=dataset_id,
                    model_name=model['Model'],
                    mse=float(model['MSE']),
                    rmse=float(model['RMSE']),
                    mae=float(model['MAE']),
                    mape=float(model['MAPE']),
                    r2=float(model['R2'])
                )
                session.add(new_metric)
        session.commit()
        print(f"Metrics for dataset {dataset_id} inserted successfully.")

        # print(metrics)
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()


# STEP 1: Select the dataset ID
dataset_id = 6
date_afn = "20150812_AFN11"

# STEP 2: Upload the predictions. Make sure the prediction file is correct
predictions_file = f"results/{date_afn}_testandscore.csv"
upload_predictions(predictions_file, dataset_id)

# STEP 3: Upload the evaluation metrics. Make sure the metrics file you are uploading is correct
metrics_file = f"results/{date_afn}_model_error_metrics.csv"
upload_metrics(metrics_file, dataset_id)
