import pandas as pd
from datetime import datetime
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models
from database_connection import Config

# Diccionario para convertir day_type de string a id
day_type_dict = {
    "Very Variable": 1,
    "Variable": 2,
    "Clear-Sky": 3,
    "Overcast": 4
}


def upload_dataset(input_file, user_id):
    """
    Uploads a dataset to the database.

    Args:
        input_file (str): The path to the CSV file containing the dataset.
        user_id (int): The ID of the user uploading the dataset.

    Returns:
        int: The ID of the newly inserted dataset.
    """
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        # Read the original CSV
        df = pd.read_csv(input_file)

        # Extract values for the necessary fields
        afn = df['AFN'].iloc[0]
        daytype = day_type_dict[df['Day_Type'].iloc[0]]

        # Calculate the window_type based on the difference between the first two rows
        time_diff = pd.to_datetime(df['Class_Datetime'].iloc[1]) - pd.to_datetime(df['Class_Datetime'].iloc[0])
        window_type = 'minuto' if time_diff.total_seconds() == 60 else 'segundo'
        description = f"Dataset de irradiancia fotovoltaica para placa {afn} con intervalo de 1 {window_type}"

        # Create a new Dataset instance
        new_dataset = models.Dataset(
            description=description,
            uploaded_by=user_id,
            active=1,
            afn=afn,
            day_type=daytype,
            window_type=window_type
        )

        # Add to the session and commit the transaction
        session.add(new_dataset)
        session.commit()

        # Retrieve the generated ID
        dataset_id = new_dataset.id
        print(f"Nuevo dataset insertado con ID: {dataset_id}")

        # Return the generated ID for use as FK in dataset_rows
        return dataset_id

    except Exception as e:
        session.rollback()
        print(f"Error al insertar el dataset: {e}")
        raise
    finally:
        session.close()


def parse_csv_to_dict_list(csv_file_path, dataset_id):
    """
    Parses a CSV file and converts it into a list of dictionaries, each representing a row in the CSV file.

    Args:
        csv_file_path (str): The path to the CSV file to be parsed.
        dataset_id (int): The ID of the dataset to which the rows belong.

    Returns:
        list: A list of dictionaries, each containing the data from a row in the CSV file.
    """
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        data = []
        for row in reader:
            data.append({
                'dataset_id': dataset_id,  # Supón que dataset_id es 1
                'day_type': day_type_dict.get(row['Day_Type'], None),  # Mapea el day_type a su id
                'afn': row['AFN'],
                'feature_0': float(row['Feature_0']),
                'feature_1': float(row['Feature_1']),
                'feature_2': float(row['Feature_2']),
                'feature_3': float(row['Feature_3']),
                'feature_4': float(row['Feature_4']),
                'feature_5': float(row['Feature_5']),
                'feature_6': float(row['Feature_6']),
                'feature_7': float(row['Feature_7']),
                'feature_8': float(row['Feature_8']),
                'feature_9': float(row['Feature_9']),
                'feature_10': float(row['Feature_10']),
                'feature_11': float(row['Feature_11']),
                'feature_12': float(row['Feature_12']),
                'feature_13': float(row['Feature_13']),
                'feature_14': float(row['Feature_14']),
                'feature_15': float(row['Feature_15']),
                'feature_16': float(row['Feature_16']),
                'feature_17': float(row['Feature_17']),
                'feature_18': float(row['Feature_18']),
                'feature_19': float(row['Feature_19']),
                'feature_20': float(row['Feature_20']),
                'feature_21': float(row['Feature_21']),
                'feature_22': float(row['Feature_22']),
                'feature_23': float(row['Feature_23']),
                'feature_24': float(row['Feature_24']),
                'feature_25': float(row['Feature_25']),
                'feature_26': float(row['Feature_26']),
                'feature_27': float(row['Feature_27']),
                'feature_28': float(row['Feature_28']),
                'feature_29': float(row['Feature_29']),
                'feature_30': float(row['Feature_30']),
                'feature_31': float(row['Feature_31']),
                'feature_32': float(row['Feature_32']),
                'feature_33': float(row['Feature_33']),
                'feature_34': float(row['Feature_34']),
                'feature_35': float(row['Feature_35']),
                'feature_36': float(row['Feature_36']),
                'feature_37': float(row['Feature_37']),
                'feature_38': float(row['Feature_38']),
                'feature_39': float(row['Feature_39']),
                'feature_40': float(row['Feature_40']),
                'feature_41': float(row['Feature_41']),
                'feature_42': float(row['Feature_42']),
                'feature_43': float(row['Feature_43']),
                'feature_44': float(row['Feature_44']),
                'feature_45': float(row['Feature_45']),
                'feature_46': float(row['Feature_46']),
                'feature_47': float(row['Feature_47']),
                'feature_48': float(row['Feature_48']),
                'feature_49': float(row['Feature_49']),
                'feature_50': float(row['Feature_50']),
                'feature_51': float(row['Feature_51']),
                'feature_52': float(row['Feature_52']),
                'feature_53': float(row['Feature_53']),
                'feature_54': float(row['Feature_54']),
                'feature_55': float(row['Feature_55']),
                'feature_56': float(row['Feature_56']),
                'feature_57': float(row['Feature_57']),
                'feature_58': float(row['Feature_58']),
                'feature_59': float(row['Feature_59']),
                'class_60': float(row['Class_60']),
                'class_day_time': datetime.strptime(row['Class_Datetime'], '%Y-%m-%d %H:%M:%S')
            })
    return data


def insert_dataset_rows(input_file, dataset_id):
    """
    Inserts rows from a CSV file into the database in batches.

    Args:
        input_file (str): The path to the CSV file containing the dataset rows.
        dataset_id (int): The ID of the dataset to which the rows belong.
    """
    # Create the engine using the Config class
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    data = parse_csv_to_dict_list(input_file, dataset_id)

    def insert_dataset_rows_in_batches(session, data, batch_size=500):
        """
        Inserts dataset rows in batches to the database.

        Args:
            session (Session): The SQLAlchemy session to use for the database operations.
            data (list): The list of dictionaries representing the dataset rows.
            batch_size (int): The number of rows to insert in each batch.
        """
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            session.bulk_insert_mappings(models.DatasetRow, batch)
            session.commit()

    try:
        insert_dataset_rows_in_batches(session, data)
        print(f"DatasetRows for dataset {dataset_id} inserted successfully.")
    except Exception as e:
        session.rollback()  # Revertir en caso de error
        print(f"Error: {e}")
    finally:
        session.close()  # Cerrar la sesión


### SUBIDA DE TODOS LOS ARCHIVOS EN CARPETA datasets_to_upload
import os
folder = "datasets_to_upload"
for file in os.listdir(folder):
    if file.endswith(".csv"):
        input_file = f"{folder}/{file}"
        user_id = 1  # ID del usuario que sube el dataset por defecto, CAMBIAR SI ES OTRO

        # Insertar dataset
        dataset_id = upload_dataset(input_file, user_id)
        # Insertar dataset_rows
        insert_dataset_rows(input_file, dataset_id)