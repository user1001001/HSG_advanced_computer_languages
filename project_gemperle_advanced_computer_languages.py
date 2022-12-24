import requests
import csv
import pandas as pd
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


class asset_info_collector:
    """
    Class to collect information about an asset via Api and web scraping
    """

    def __init__(self, symbol, api='demo'):
        """
        Initialize the main Attributes of the class
        """
        self._api = api  # Store the api
        self.symbol_list = asset_info_collector.fetch_symbol_list(api)  # Set a a sample list of the symbols
        self.symbol = symbol  # Store the symbol
        self.time_series = None  # Create two empty values for storage
        self.info = None
        self.fetch_time_series()  # Fill the two empty values
        self.overview = None  # Create empty values for storage
        self.fetch_overview()  # Fill the empty value
        self.name = self.overview.loc['Name'].values[0]  # Store the corresponding name from the symbol
        self.log_return = np.log(self.time_series['Close'].iloc[::-1]) - np.log(
            self.time_series['Close'].iloc[::-1].shift(1))  # Calculate and store the log return

    @staticmethod
    def fetch_symbol_list(api='demo'):  # See if names is preset!
        """
        Download of a example symbol list via API (callable without an object)
        """
        CSV_URL = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api}'
        with requests.Session() as s:
            download = s.get(CSV_URL)  # Donwload file
            decoded_content = download.content.decode('utf-8')  # Decode File
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')  # Read csv file
            df_symbol = pd.DataFrame(cr)  # Store it in a Dataframe
            df_symbol.columns = df_symbol.iloc[0]  # Set column names
            df_symbol = df_symbol.loc[df_symbol['assetType'] == 'Stock'][
                        1:].reset_index()  # Sort table and only keep stocks
        return df_symbol

    @property  # Function if corresponding attribute is called
    def symbol(self):
        return self._symbol

    @symbol.setter  # Function if corresponding attribute is set
    def symbol(self, val):
        if val not in self.symbol_list['symbol'].values:  # Check if entered symbol is supported
            raise ValueError(
                'Please enter a valid symbol or take a look at the symbol list (asset_info_collector..fetch_symbol_list())'
            )  # Raise Error if it is not supportet
        self._symbol = val

    @property  # Function if corresponding attribute is called
    def api(self):
        return self._api

    def fetch_time_series(self):
        """
        Download of the corresponding time series data for the given symbol from Alpha Vantage
        """
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={self.symbol}&apikey={self._api}'
        r = requests.get(url)  # Get data
        data = r.json()  # Read/decode data
        self.time_series = pd.DataFrame(data["Weekly Time Series"],
                                        dtype='float').T  # Store data in Dataframe
        self.time_series.columns = ['Open', 'High', 'Low', 'Close', 'Volume']  # Set column names
        self.time_series.index = pd.to_datetime(self.time_series.index)  # Transform index to datetime
        self.info_time_series = pd.DataFrame(data["Meta Data"],
                                             index=['Meta Data']).T  # Store second table in Dataframe

    def statistics(self):
        """
        Function which returns basic descriptive statistics from time series Dataframe
        """
        return self.time_series.describe(include='all')

    def fetch_overview(self):
        """
        Download of the corresponding general infos for the given symbol from Alpha Vantage
        """
        url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={self.symbol}&apikey={self._api}'
        r = requests.get(url)  # Get data
        data = r.json()  # Read/decode data
        self.overview = pd.DataFrame(data, index=['Data']).T  # Store data in Dataframe

    def income_statement(self, annual=False):
        """
        Download of the corresponding income statement for the given symbol from Alpha Vantage
        """
        url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={self.symbol}&apikey={self._api}'
        r = requests.get(url)  # Get data
        data = r.json()  # Read/decode data
        annual_reports = pd.DataFrame(data["annualReports"])  # Store data in Dataframe
        quarterly_reports = pd.DataFrame(data["quarterlyReports"])  # Store second table in Dataframe
        if annual == True:  # Check input value and return corresponding Dataframe
            return annual_reports
        else:
            return quarterly_reports

    def balace_sheet(self, annual=False):
        """
        Download of the corresponding balance sheet for the given symbol from Alpha Vantage
        """
        url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={self.symbol}&apikey={self._api}'
        r = requests.get(url)  # Get data
        data = r.json()  # Read/decode data
        annual_reports = pd.DataFrame(data["annualReports"])  # Store data in Dataframe
        quarterly_reports = pd.DataFrame(data["quarterlyReports"])  # Store second table in Dataframe
        if annual == True:  # Check input value and return corresponding Dataframe
            return annual_reports
        else:
            return quarterly_reports

    def cashflow(self, annual=False):
        """
        Download of the corresponding cashflow for the given symbol from Alpha Vantage
        """
        url = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={self.symbol}&apikey={self._api}'
        r = requests.get(url)  # Get data
        data = r.json()  # Read/decode data
        annual_reports = pd.DataFrame(data["annualReports"])  # Store data in Dataframe
        quarterly_reports = pd.DataFrame(data["quarterlyReports"])  # Store second table in Dataframe
        if annual == True:  # Check input value and return corresponding Dataframe
            return annual_reports
        else:
            return quarterly_reports

    def earnings(self, annual=False):
        """
        Download of the corresponding earnings for the given symbol from Alpha Vantage
        """
        url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={self.symbol}&apikey={self._api}'
        r = requests.get(url)  # Get data
        data = r.json()  # Read/decode data
        annual_earnings = pd.DataFrame(data["annualEarnings"])  # Store data in Dataframe
        quarterly_earnings = pd.DataFrame(data["quarterlyEarnings"])  # Store second table in Dataframe
        if annual == True:  # Check input value and return corresponding Dataframe
            return annual_earnings
        else:
            return quarterly_earnings

    def current_news(self, key_val=None):
        """
        Function to get a list of links from marketnews for a given key word
        Default: it is searching for the symbol of the Stock or the name of the company
        """
        url = 'https://marketnews.com/'

        # Excess site
        request = requests.get(url, headers={'User-agent': 'Chrome/39.0.2171.95'})
        html = request.content
        soup = BeautifulSoup(html, 'lxml')

        # Check if key value is defined otherwise set it to the default keys
        if key_val == None:
            key_val = [self.symbol, self.name]

        # Create empty lists
        directory_list = []
        list_link = []

        # Check if a list or a string is given
        if type(key_val) == list:
            for key in key_val:  # Iterate over list values
                directory = soup.findAll(
                    'a',
                    class_='widget__headline-text custom-post-headline',
                    text=re.compile(key, re.IGNORECASE))  # Store individual resultts of the keys
                directory_list.extend(directory)  # Add results to list
        else:
            directory_list = soup.findAll(
                'a',
                class_='widget__headline-text custom-post-headline',
                text=re.compile(key, re.IGNORECASE))  # Store results for string

        # Check if there are multiple results or just one
        if type(directory_list) == list:
            for directory in directory_list:  # Iterate over list values
                link = (directory.get('href'))  # Get links
                print(link)  # Print links
        else:
            link = (directory_list.get('href'))  # Get link
            print(link)  # Print link

    def plot_closing_price(self):
        """
        Function to plot the closing price
        """
        fig = sns.lineplot(
            data=self.time_series['Close'].iloc[::-1],
            color='darkblue').set(title=f'Closing Price {self.symbol}')  # Define plot and set title
        plt.xlabel('Time')  # Set x-label
        plt.ylabel('Closing Price')  # Set y-label
        plt.show()

    def plot_log_return(self):
        """
        Function to plot the log return
        """
        fig = sns.lineplot(data=self.log_return,
                           color='darkblue').set(title=f'Log Return {self.symbol}')  # Define plot and set title
        plt.xlabel('Time')  # Set x-label
        plt.ylabel('Log Return')  # Set y-label
        plt.show()

    def plot_volume(self):
        """
        Function to plot the volume
        """
        fig = sns.lineplot(data=self.time_series['Volume'].iloc[::-1],
                           color='darkblue').set(title=f'Volume {self.symbol}')  # Define plot and set title
        plt.xlabel('Time')  # Set x-label
        plt.ylabel('Volume')  # Set y-label
        plt.show()

    def save(self, form='excel', name=None, path=''):
        """
        Function to export the time series table to an excel or csv file
        """
        # Check if name is defined otherwise set it to the default name
        if name == None:
            name = f'df_{self.symbol}'

        # Check input value and save it in corresponding file type
        if form == 'excel':
            path_name = path + name + '.xlsx'  # combine path, name and type specific ending in string
            self.time_series.to_excel(path_name)  # Save table in excel file
        elif form == 'csv':
            path_name = path + name + '.csv'  # combine path, name and type specific ending in string
            self.time_series.to_csv(path_name)  # Save table in csv file
        else:
            raise ValueError('Please choose a upported format (Excel or CSV)')  # Raise error if other file type is past
