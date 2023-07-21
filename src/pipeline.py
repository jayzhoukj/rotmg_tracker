import numpy as np
import pandas as pd

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.helpers.webscraping_utils import (
    get_text
)


def webscraping_pipeline(data_limit: int = 200):
    # Scraping
    url = 'https://realmstock.com/pages/event-notifier'

    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')

    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.get(url=url)

    na_threshold = 3
    na_count = 0

    all_status = []
    all_rem_counts = []
    all_data_timestamps = []

    for i in range(data_limit):
        
        if na_count >= na_threshold:
            break
        
        status = get_text(
            driver=driver,
            xpath=f'//*[@id="history"]/div[{i}]/div/table/tbody/tr/td[1]',
            wait_duration=2
        )

        rem_count = get_text(
            driver=driver,
            xpath=f'//*[@id="history"]/div[{i}]/div/table/tbody/tr/td[2]',
            wait_duration=1.5
        )

        data_timestamp = get_text(
            driver=driver,
            xpath=f'//*[@id="history"]/div[{i}]/div/table/tbody/tr/td[3]'
        )

        all_status.append(status)
        all_rem_counts.append(rem_count)
        all_data_timestamps.append(data_timestamp)

        if status == 'N/A':
            na_count += 1

    data_collected_time = str(pd.Timestamp.now())

    # Data Processing
    df = pd.DataFrame(
        data={
            'status': all_status,
            'rem_counts': all_rem_counts,
            'data_timestamp': all_data_timestamps
        }
    ).sort_values(
        by=['data_timestamp'],
        ascending=False
    )

    return df, data_collected_time


def data_processing_pipeline(df: pd.DataFrame):
    df = df[
        (
            df['status'] != 'N/A'
        ) & (
            df['rem_counts'] != 'N/A'
        )
    ]

    df['server'] = df['status'].apply(lambda status: status.split(' ', 2)[0])
    df['realm'] = df['status'].apply(lambda status: status.split(' ', 2)[1])
    df['n_players'] = df['status'].apply(lambda status: status.split(' ', 2)[2].rsplit('/', 1)[0])
    df['max_players'] = df['status'].apply(lambda status: status.split(' ', 2)[2].rsplit('/', 1)[-1])

    def extract_rem_count(text):
        if 'Events' in text:
            try:
                output = int(text.split('Events')[0].strip())

            except:
                output = np.nan

        else:
            output = np.nan

        return output

    df['n_events_rem'] = df['rem_counts'].apply(extract_rem_count)

    df = df[
        (
            df['realm'] != 'Nexus'
        ) & (
            df['server'] != 'EUWest'
        ) & (
            df['server'] != 'USEast'
        ) & (
            df['n_events_rem'] > 0
        ) & (
            df['n_events_rem'] <= 15
        )
    ].drop(
        columns=[
            'status',
            'rem_counts'
        ]
    )

    df['n_events_rem'] = df['n_events_rem'].apply(int)
    df['n_players'] = df['n_players'].apply(int)

    # Setting calculation parameters
    events_weight = 0.8
    players_weight = 0.2

    max_realm_events = 50
    max_realm_players = 85

    # Calculate score for realm feasibility for o3 runs
    df['score'] = (
        (
            df['n_events_rem'] / max_realm_events
        ) * events_weight
    ) + (
        (
            df['n_players'] / max_realm_players
        ) * players_weight
    )

    df = df.sort_values(
        by=[
            'score',
            'n_events_rem',
            'n_players'
        ],
        ascending=True
    ).drop_duplicates(
        subset=['server', 'realm'],
        keep='first'
    )

    col_order = [
        'server',
        'realm',
        'n_events_rem',
        'n_players',
        'score'
    ]

    df = df[col_order].copy()

    df_potential_runs = df.copy(deep=True)

    # Set calculation parameters
    events_weight = 0.2
    players_weight = 0.8

    max_realm_events = 50
    max_realm_players = 85

    # Calculate score for ranking potential o3 runs
    df_potential_runs['score'] = (
        (
            (
                max_realm_events - df['n_events_rem']
            ) / max_realm_events
        ) * events_weight
    ) + (
        (
            df['n_players'] / max_realm_players
        ) * players_weight
    )

    df_potential_runs.sort_values(
        by=['score'],
        ascending=False,
        inplace=True
    )

    return df, df_potential_runs


