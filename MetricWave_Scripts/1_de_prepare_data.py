import os
import numpy as np
import pandas as pd

intervals = ['1min', '1s']
pd.set_option('display.max_columns', None)


def create_equidistance(df_origin, interval):
    """
        Create a DataFrame with equidistant time intervals.

        Args:
            df_origin (DataFrame): Original DataFrame.
            interval (str): Time interval ('1min' or '1s').

        Returns:
            DataFrame: DataFrame with equidistant time intervals.
    """
    # Convierte las columnas de Fecha y Timestamp en un objeto de fecha y hora único (Hace falta para reindexar y los intervalos)
    df_origin['DateTime'] = pd.to_datetime(df_origin['Date (yyyy-mm-dd)'] + ' ' + df_origin['Timestamp (hh:mm:ss.nnn)'])

    # Reindexa el DataFrame para tener un índice de tiempo continuo con un intervalo de 10 milisegundos
    idx = pd.date_range(start=df_origin['DateTime'].min(), end=df_origin['DateTime'].max(), freq='10ms')
    # Genera un indice nuevo para todos los que no tiene match en el dataset df_origin
    df_origin = df_origin.set_index('DateTime').reindex(idx)
    # Rellena los valores faltantes dentro de cada segundo con el valor correspondiente de la medición anterior
    df_origin = df_origin.ffill()
    # Filtra el DataFrame para dejar solo las filas únicas (coge la primera)
    df_by_interval = df_origin.resample(interval).first()

    # Agrupa los datos por segundo y calcula la suma para cada segundo
    sum_by_interval = df_origin.resample(interval).sum()

    # Borra las columnas y vuelve a anadirlas. Daba fallo al reescribirlas
    df_by_interval.drop(['G1 (W/m2)', 'G2 (W/m2)'], axis=1, inplace=True)
    df_by_interval = pd.merge(df_by_interval, sum_by_interval[['G1 (W/m2)', 'G2 (W/m2)']], left_index=True,
                              right_index=True)
    df_by_interval['Timestamp (hh:mm:ss.nnn)'] = sum_by_interval.index.time.astype(str)
    print("\tEquidistant data created for interval", interval, "with", len(df_by_interval), "rows.")
    return df_by_interval


def get_days_type():
    """
    Get day types.

    Returns:
        dict: Dictionary of day types.
    """
    return {'20150324': 'Clear-Sky', '20150208': 'Overcast', '20151008': 'Variable', '20150812': 'Very Variable'}


def get_day_type_and_afn(filename):
    """
    Get day type and AFN value from filename.

    Args:
        filename (str): File name.

    Returns:
        tuple: Day type and AFN value.
    """
    f_split = filename.split('_')
    date = f_split[0]
    afn = f_split[1].split(".")[0]

    return get_days_type()[date], afn


def add_day_type_and_afn(filename, dataframe):
    """
        Add day type and AFN value to DataFrame.

        Args:
            filename (str): File name.
            dataframe (DataFrame): DataFrame to which data will be added.

        Returns:
            DataFrame: DataFrame with day type and AFN value added.
    """
    day_type, afn = get_day_type_and_afn(filename)
    dataframe.insert(0, 'DayType', day_type)
    dataframe.insert(1, "AFN", afn)
    return dataframe


def process_data():
    """
       Process CSV files stored in Original files and save processed equidistant data.
    """
    num_files = 0
    for filename in os.listdir(pathOriginal):
        df = pd.read_csv(os.path.join(pathOriginal, filename))
        for i in intervals:
            num_files += 1
            file_path = os.path.join("Alderville " + i, filename)
            print(num_files, "- Processing", filename, "for interval", i, "...")

            df_processed = create_equidistance(df, i)
            df_processed = add_day_type_and_afn(filename, df_processed)
            df_processed.to_csv(file_path, index=False)


def generate_features_manually(path):
    """
    Generates and saves feature vectors from CSV files located in the given directory.

    This function reads each CSV file in the given directory, extracts features based on a 60 points window size,
    and concatenates these features with the class label (point 61) and timestamp to form a complete feature set.
    The resulting DataFrame is saved in a subdirectory as a new CSV file.

    Args:
        path (str): Path to the directory containing the CSV files to process.

    """
    window_size = 60  # Defines the number of points in each window (e.g., 60 minutes or seconds)

    try:
        for filename in os.listdir(path):
            print("Generating", path, filename, "features...")
            df = pd.read_csv(os.path.join(path, filename))
            df['DateTime'] = pd.to_datetime(df['Date (yyyy-mm-dd)'] + ' ' + df['Timestamp (hh:mm:ss.nnn)'])
            dataset = []  # Initialize an empty list to store the feature vectors

            for start in range(len(df) - window_size):
                end = start + window_size
                # Extract features from the penultimate column in the specified window
                window_features = df.iloc[start:end, len(df.columns) - 2:len(df.columns) - 1].values.flatten()
                # Extract class value from the last column at the end of the window
                class_value = df.iloc[end, len(df.columns) - 2:].values.flatten()
                row = np.concatenate((window_features, class_value), axis=0)
                dataset.append(row)

            # Create DataFrame from the collected data
            final = pd.DataFrame(data=dataset)
            # Assuming a function that adds 'Day_Type' and 'AFN' columns based on filename
            final = add_day_type_and_afn(filename, final)
            # Generate column names for features and labels
            feature_names = ['Feature_' + str(i) for i in range(0, window_size)]
            column_names = ["Day_Type", "AFN"] + feature_names + ["Class_" + str(window_size), "Class_Datetime"]
            final.columns = column_names
            # Save the final DataFrame to a new CSV file in a subdirectory
            final.to_csv(os.path.join(path + " Features", filename))
        print("\nFeatures created\n")
    except Exception as err:
        print("Error:", err)
        print("Check if file format is correct?")


pathOriginal = "Alderville - Original"
path1s = "Alderville 1s"
path1min = "Alderville 1min"

# STEP 1: Process data stored in pathOriginal to create equidistance in all files
# process_data()
# Generates the features for both folders previously created
# generate_features_manually(path1s)
generate_features_manually(path1min)
# generate_features_manually(path1s)
