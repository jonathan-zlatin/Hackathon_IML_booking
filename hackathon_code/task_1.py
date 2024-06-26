import pandas as pd
import numpy as np
from hackathon_code import utils
from sklearn.tree import DecisionTreeClassifier
from hackathon_code.ModelBaseline import BaselineModel
import plotly.io as pio

pio.renderers.default = 'browser'


def replace_none_with_samples(data, dict):
    """
        Replace None values in the DataFrame with generated samples from the given dictionary.

        Args:
        - data (pd.DataFrame): The DataFrame to be processed.
        - dict (dict): Dictionary containing generated samples for each column.

        Returns:
        - pd.DataFrame: The DataFrame with None values replaced by generated samples.
        """
    # Iterate over each column
    for column in data.columns:
        # Replace None values with the generated samples
        data.loc[data[column].isna(), column] = dict[column]

    return data


def preprocess(X: pd.DataFrame, y: pd.DataFrame, dict):
    """
        Preprocess the input DataFrame for task 1.

        Args:
        - X (pd.DataFrame): The input DataFrame.
        - y (pd.DataFrame): The target DataFrame.
        - dict (dict): Dictionary containing generated samples for each column.

        Returns:
        - pd.DataFrame: Preprocessed input DataFrame X.
        - pd.DataFrame: Target DataFrame y.
        """
    # Replace None values
    X = replace_none_with_samples(X, dict)
    # Convert the 'checkin_date' and 'booking_datetime' columns to datetime type
    X['checkin_date'] = pd.to_datetime(X['checkin_date'])
    X['booking_datetime'] = pd.to_datetime(X['booking_datetime'])
    X = utils.convert_cancellation_code_to_columns(X)
    # Calculate the difference in days between 'checkin_date' and 'booking_datetime'
    X['days_before_checkin'] = (X['checkin_date'] - X['booking_datetime']).dt.days + 1

    X.drop(["h_customer_id", "customer_nationality", "origin_country_code",
            "language", "original_payment_currency", "is_user_logged_in",
            "hotel_area_code", "booking_datetime", "checkin_date", "checkout_date",
            "hotel_live_date", "request_nonesmoke", 'request_latecheckin', "request_highfloor", "request_twinbeds",
            "request_airport", "request_earlycheckin", "request_largebed", "hotel_country_code",
            "guest_nationality_country_name",
            "hotel_brand_code", "hotel_chain_code", "hotel_city_code"], axis=1, inplace=True)

    X["accommadation_type_name"] = np.where(X["accommadation_type_name"].isin(["Hotel",
                                                                               "Guest House / Bed & Breakfast",
                                                                               "Hostel", "Resort"]),
                                            X["accommadation_type_name"], 'other')
    X["charge_option"] = np.where(X["charge_option"] == "Pay at Check-in", "Pay Later",
                                  X["charge_option"])
    X["original_payment_method"] = np.where(X["original_payment_method"].isin(["Visa",
                                                                               "MasterCard", "American Express"]),
                                            X["original_payment_method"], 'other')

    X = pd.get_dummies(X, columns=["accommadation_type_name", "charge_option", "original_payment_type",
                                   "original_payment_method"])
    if y is None:
        return X
    return X, y[X.index]


def get_mean_dictionary(data):
    """
        Generate a dictionary with mean values for each column.

        Args:
        - data (pd.DataFrame): The input DataFrame.

        Returns:
        - dict: Dictionary containing mean values for each column.
        """
    # Iterate over each column
    dict = {}
    for column in data.columns:
        dict[column] = data[column].value_counts().index[0]

    return dict


def run_task_1(df: pd.DataFrame, dict: dict):
    """
        Run task 1.

        Args:
        - df (pd.DataFrame): The input DataFrame.
        - dict (dict): Dictionary containing mean values for each column.

        Returns:
        - BaselineModel: Trained BaselineModel for task 1.
        """
    X, y = df.drop("cancellation_datetime", axis=1), df["cancellation_datetime"]
    y = np.where(y.isnull(), 0, 1)
    X_train, y_train = preprocess(X, y, dict)

    estimator = DecisionTreeClassifier(max_depth=1)
    model = BaselineModel(estimator, 200)
    model.fit(X_train, y_train)
    return model
