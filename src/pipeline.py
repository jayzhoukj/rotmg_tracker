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

    driver = Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.get(url=url)

    na_threshold = 3
    na_count = 0

    all_status = []
    all_rem_counts = []

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

        all_status.append(status)
        all_rem_counts.append(rem_count)

        if status == 'N/A':
            na_count += 1

    data_collected_time = str(pd.Timestamp.now())

    # Data Processing
    df = pd.DataFrame(
        data={
            'status': all_status,
            'rem_counts': all_rem_counts
        }
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
            output = int(text.split('Events')[0].strip())

        else:
            output = np.nan

        return output

    df['n_events_rem'] = df['rem_counts'].apply(extract_rem_count)

    df = df[
        (
            df['realm'] != 'Nexus'
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

    df['score'] = df['n_events_rem'] * 0.8 + df['n_players'] * 0.2

    df = df.sort_values(
        by=[
            'score',
            'n_events_rem',
            'n_players'
        ],
        ascending=True
    ).drop_duplicates(
        subset=['server', 'realm'],
        keep='last'
    )

    col_order = [
        'server',
        'realm',
        'n_events_rem',
        'n_players',
        'score'
    ]

    df = df[col_order].copy()

    return df


