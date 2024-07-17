<<<<<<< HEAD
import pandas as pd
import numpy as np

class MissingValueError(Exception):
    """Exception raised for missing values in the dataframe."""
    
    def __init__(self, message: str = "Missing values found"):
        self.message = message
        super().__init__(self.message)


class DuplicateValueError(Exception):
    """Exception raised for duplicate values in the dataframe."""
    
    def __init__(self, message: str = "Duplicate values found"):
        self.message = message
        super().__init__(self.message)


class DataFrameValidator:
    """
    A class to validate a pandas DataFrame for missing and duplicate values in the 'Local time' column.

    Attributes:
    ----------
    dataframe : pd.DataFrame
        The DataFrame to be validated.
    __missing_indices : list
        Indices of rows with missing 'Local time' values.
    __duplicate_indices : list
        Indices of rows with duplicate 'Local time' values.
    """
    
    time_intervals = {
            1: "1s",
            30: "30s",
            60: "1min",
            300: "5min",
            600: "10min",
            900: "15min",
            3600: "1h",
            7200: "2h",
            14400: "4h",
            21600: "6h",
            86400: "1d",
            604800: "1w",
            2592000: "1m",
            31536000: "1y"
        }
    
    
    def __init__(self, dataframe: pd.DataFrame) -> None:
        """
        Initializes the DataFrameValidator with a DataFrame and initializes lists for missing and duplicate indices.

        Parameters:
        ----------
        dataframe : pd.DataFrame
            The DataFrame to be validated.
        """
        self.dataframe = dataframe
        self.timeframe = ''
        self        
        self.__missing_indices = []
        self.__duplicate_indices = []
        
    def find_missing_values(self) -> bool:
        """
        Finds and records indices of missing values in the 'Local time' column.

        Returns:
        -------
        bool
            True if there are missing values, False otherwise.
        """
        missing = self.dataframe[self.dataframe['Local time'].isna()].index.tolist()
        self.__missing_indices = missing
        return len(missing) > 0

    def find_duplicate_values(self) -> bool:
        """
        Finds and records indices of duplicate values in the 'Local time' column.

        Returns:
        -------
        bool
            True if there are duplicate values, False otherwise.
        """
        duplicates = self.dataframe[self.dataframe.duplicated(subset=['Local time'], keep=False)].index.tolist()
        self.__duplicate_indices = duplicates
        return len(duplicates) > 0
    
    def is_valid(self) -> bool:
        """
        Checks for missing and duplicate values in the 'Local time' column.
        
        Raises:
        ------
        MissingValueError
            If missing values are found.
        DuplicateValueError
            If duplicate values are found.

        Returns:
        -------
        bool
            True if there are no missing or duplicate values.
        """
        if self.find_missing_values():
            raise MissingValueError(f"Missing values found at indices: {self.__missing_indices}")
        elif self.find_duplicate_values():
            raise DuplicateValueError(f"Duplicate values found at indices: {self.__duplicate_indices}")
        else:
            return True
        
        
    def calculate_timeframe(self):
        """
        Calculate the time interval between consecutive rows in a DataFrame.
        
        This function parses the 'Local time' column into datetime objects, 
        calculates the time difference between the first two rows, and returns 
        the interval in a human-readable format showing hours, minutes, and seconds.

        Returns:
        str: The time difference between consecutive rows formatted as 'X hours, Y minutes, and Z seconds'.
        
        Example:
        data = {
            'Local time': [
                '01.01.2023 00:00:00.000 GMT+0330',
                '01.01.2023 00:01:00.000 GMT+0330',
                '01.01.2023 00:02:00.000 GMT+0330',
                '01.01.2023 00:03:00.000 GMT+0330',
                '01.01.2023 00:04:00.000 GMT+0330'
            ],
            'Open': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
            'High': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
            'Low': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
            'Close': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
            'Volume': [0.01, 0.02, 0.03, 0.04, 0.05]
        }
        validator = DataframeValidator(data)
        validator.calculate_timeframe()
        '0 hours, 1 minutes, 0 seconds'
        """
        
        # Parse the 'Local time' column into datetime objects
        self.dataframe['Local time'] = pd.to_datetime(self.dataframe['Local time'], format='%d.%m.%Y %H:%M:%S.%f GMT%z')
        
        # Calculate the difference between the first two rows
        time_diff = self.dataframe['Local time'].diff().dropna().iloc[0]
        
        # Extract hours, minutes, and seconds from the time difference
        total_seconds = time_diff.total_seconds()
        

        # Try to match the total seconds to a supported interval
        for interval, interval_str in DataFrameValidator.time_intervals.items():
            if total_seconds == interval:
                self.timeframe = interval_str
                return interval_str

        # Raise an error if no exact match is found
        raise ValueError(f"Time difference ({total_seconds} seconds) doesn't match a supported interval.")
    
    
    
    def get_missing_indices(self) -> list:
        """
        Returns the indices of missing values in the 'Local time' column.

        Returns:
        -------
        list
            Indices of missing values.
        """
        return self.__missing_indices


    def get_duplicate_indices(self) -> list:
        """
        Returns the indices of duplicate values in the 'Local time' column.

        Returns:
        -------
        list
            Indices of duplicate values.
        """
        return self.__duplicate_indices

    def remove_duplicates(self) -> None:
        """
        Removes duplicate rows in the DataFrame, keeping the first occurrence.
        """
        self.dataframe.drop_duplicates(subset=['Local time'], inplace=True)
        self.dataframe.sort_values(by='Local time', inplace=True)
        self.dataframe.reset_index(drop=True, inplace=True)
        self.__duplicate_indices = []  # Reset dupclicate indices indices after duplicate removal



    def remove_missings(self) -> None:
        """
            Fills missing 'Local time' values with a continuous time series.

            This method generates a new 'Local time' series based on the first valid time and the detected time interval,
            then replaces the existing 'Local time' column with this continuous series.

            Raises:
            -------
            ValueError
                If the detected time interval is unsupported.

            Example:
            --------
            data = {
                'Local time': [
                    '01.01.2023 00:00:00.000 GMT+0330',
                    None,
                    '01.01.2023 00:02:00.000 GMT+0330',
                    '01.01.2023 00:03:00.000 GMT+0330',
                    '01.01.2023 00:04:00.000 GMT+0330'
                ],
                'Open': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
                'High': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
                'Low': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
                'Close': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
                'Volume': [0.01, 0.02, 0.03, 0.04, 0.05]
            }
            validator = DataFrameValidator(pd.DataFrame(data))
            validator.calculate_timeframe()
            '0 hours, 1 minutes, 0 seconds'
            validator.remove_missings()
        """
        first_valid_index = self.dataframe['Local time'].first_valid_index()

        # Determine the appropriate time interval string
        time_interval = 0

        for seconds, interval in DataFrameValidator.time_intervals.items():
            if self.timeframe == interval:
                time_interval = seconds
                break

        if time_interval is None:
            raise ValueError("Unsupported time interval detected")

        # Calculate the initial `Local time` for the first row
        initial_time = self.dataframe.loc[first_valid_index, 'Local time'] - pd.to_timedelta(first_valid_index * time_interval, unit='s')

        # Generate the entire `Local time` series
        new_local_time_series = pd.date_range(start=initial_time, periods=len(self.dataframe), freq=self.timeframe)

        # Replace the `Local time` column with the newly generated series
        self.dataframe['Local time'] = new_local_time_series
=======
import pandas as pd
import numpy as np

class MissingValueError(Exception):
    """Exception raised for missing values in the dataframe."""
    
    def __init__(self, message: str = "Missing values found"):
        self.message = message
        super().__init__(self.message)


class DuplicateValueError(Exception):
    """Exception raised for duplicate values in the dataframe."""
    
    def __init__(self, message: str = "Duplicate values found"):
        self.message = message
        super().__init__(self.message)


class DataFrameValidator:
    """
    A class to validate a pandas DataFrame for missing and duplicate values in the 'Local time' column.

    Attributes:
    ----------
    dataframe : pd.DataFrame
        The DataFrame to be validated.
    __missing_indices : list
        Indices of rows with missing 'Local time' values.
    __duplicate_indices : list
        Indices of rows with duplicate 'Local time' values.
    """
    
    time_intervals = {
            1: "1s",
            30: "30s",
            60: "1min",
            300: "5min",
            600: "10min",
            900: "15min",
            3600: "1h",
            7200: "2h",
            14400: "4h",
            21600: "6h",
            86400: "1d",
            604800: "1w",
            2592000: "1m",
            31536000: "1y"
        }
    
    
    def __init__(self, dataframe: pd.DataFrame) -> None:
        """
        Initializes the DataFrameValidator with a DataFrame and initializes lists for missing and duplicate indices.

        Parameters:
        ----------
        dataframe : pd.DataFrame
            The DataFrame to be validated.
        """
        self.dataframe = dataframe
        self.timeframe = ''
        self        
        self.__missing_indices = []
        self.__duplicate_indices = []
        
    def find_missing_values(self) -> bool:
        """
        Finds and records indices of missing values in the 'Local time' column.

        Returns:
        -------
        bool
            True if there are missing values, False otherwise.
        """
        missing = self.dataframe[self.dataframe['Local time'].isna()].index.tolist()
        self.__missing_indices = missing
        return len(missing) > 0

    def find_duplicate_values(self) -> bool:
        """
        Finds and records indices of duplicate values in the 'Local time' column.

        Returns:
        -------
        bool
            True if there are duplicate values, False otherwise.
        """
        duplicates = self.dataframe[self.dataframe.duplicated(subset=['Local time'], keep=False)].index.tolist()
        self.__duplicate_indices = duplicates
        return len(duplicates) > 0
    
    def is_valid(self) -> bool:
        """
        Checks for missing and duplicate values in the 'Local time' column.
        
        Raises:
        ------
        MissingValueError
            If missing values are found.
        DuplicateValueError
            If duplicate values are found.

        Returns:
        -------
        bool
            True if there are no missing or duplicate values.
        """
        if self.find_missing_values():
            raise MissingValueError(f"Missing values found at indices: {self.__missing_indices}")
        elif self.find_duplicate_values():
            raise DuplicateValueError(f"Duplicate values found at indices: {self.__duplicate_indices}")
        else:
            return True
        
        
    def calculate_timeframe(self):
        """
        Calculate the time interval between consecutive rows in a DataFrame.
        
        This function parses the 'Local time' column into datetime objects, 
        calculates the time difference between the first two rows, and returns 
        the interval in a human-readable format showing hours, minutes, and seconds.

        Returns:
        str: The time difference between consecutive rows formatted as 'X hours, Y minutes, and Z seconds'.
        
        Example:
        data = {
            'Local time': [
                '01.01.2023 00:00:00.000 GMT+0330',
                '01.01.2023 00:01:00.000 GMT+0330',
                '01.01.2023 00:02:00.000 GMT+0330',
                '01.01.2023 00:03:00.000 GMT+0330',
                '01.01.2023 00:04:00.000 GMT+0330'
            ],
            'Open': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
            'High': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
            'Low': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
            'Close': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
            'Volume': [0.01, 0.02, 0.03, 0.04, 0.05]
        }
        validator = DataframeValidator(data)
        validator.calculate_timeframe()
        '0 hours, 1 minutes, 0 seconds'
        """
        
        # Parse the 'Local time' column into datetime objects
        self.dataframe['Local time'] = pd.to_datetime(self.dataframe['Local time'], format='%d.%m.%Y %H:%M:%S.%f GMT%z')
        
        # Calculate the difference between the first two rows
        time_diff = self.dataframe['Local time'].diff().dropna().iloc[0]
        
        # Extract hours, minutes, and seconds from the time difference
        total_seconds = time_diff.total_seconds()
        

        # Try to match the total seconds to a supported interval
        for interval, interval_str in DataFrameValidator.time_intervals.items():
            if total_seconds == interval:
                self.timeframe = interval_str
                return interval_str

        # Raise an error if no exact match is found
        raise ValueError(f"Time difference ({total_seconds} seconds) doesn't match a supported interval.")
    
    
    
    def get_missing_indices(self) -> list:
        """
        Returns the indices of missing values in the 'Local time' column.

        Returns:
        -------
        list
            Indices of missing values.
        """
        return self.__missing_indices


    def get_duplicate_indices(self) -> list:
        """
        Returns the indices of duplicate values in the 'Local time' column.

        Returns:
        -------
        list
            Indices of duplicate values.
        """
        return self.__duplicate_indices

    def remove_duplicates(self) -> None:
        """
        Removes duplicate rows in the DataFrame, keeping the first occurrence.
        """
        self.dataframe.drop_duplicates(subset=['Local time'], inplace=True)
        self.dataframe.sort_values(by='Local time', inplace=True)
        self.dataframe.reset_index(drop=True, inplace=True)
        self.__duplicate_indices = []  # Reset dupclicate indices indices after duplicate removal



    def remove_missings(self) -> None:
        """
            Fills missing 'Local time' values with a continuous time series.

            This method generates a new 'Local time' series based on the first valid time and the detected time interval,
            then replaces the existing 'Local time' column with this continuous series.

            Raises:
            -------
            ValueError
                If the detected time interval is unsupported.

            Example:
            --------
            data = {
                'Local time': [
                    '01.01.2023 00:00:00.000 GMT+0330',
                    None,
                    '01.01.2023 00:02:00.000 GMT+0330',
                    '01.01.2023 00:03:00.000 GMT+0330',
                    '01.01.2023 00:04:00.000 GMT+0330'
                ],
                'Open': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
                'High': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
                'Low': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
                'Close': [1.0711, 1.0711, 1.0711, 1.0711, 1.0711],
                'Volume': [0.01, 0.02, 0.03, 0.04, 0.05]
            }
            validator = DataFrameValidator(pd.DataFrame(data))
            validator.calculate_timeframe()
            '0 hours, 1 minutes, 0 seconds'
            validator.remove_missings()
        """
        first_valid_index = self.dataframe['Local time'].first_valid_index()

        # Determine the appropriate time interval string
        time_interval = 0

        for seconds, interval in DataFrameValidator.time_intervals.items():
            if self.timeframe == interval:
                time_interval = seconds
                break

        if time_interval is None:
            raise ValueError("Unsupported time interval detected")

        # Calculate the initial `Local time` for the first row
        initial_time = self.dataframe.loc[first_valid_index, 'Local time'] - pd.to_timedelta(first_valid_index * time_interval, unit='s')

        # Generate the entire `Local time` series
        new_local_time_series = pd.date_range(start=initial_time, periods=len(self.dataframe), freq=self.timeframe)

        # Replace the `Local time` column with the newly generated series
        self.dataframe['Local time'] = new_local_time_series
>>>>>>> 2033d87bd8f4bf6c10f6fb586bc7b9dbbdf238dc
        