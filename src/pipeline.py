import numpy as np
import pandas as pd

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.helpers.webscraping_utils import (
    get_text
)
from src.helpers.data_utils import (
    data_cleaning,
    calculate_realm_feasibility,
    calculate_potential_runs,
    tier_2_deduplication
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
    df, df_nexus = data_cleaning(df=df)

    df_all_servers = pd.DataFrame(
        {
            'server': [
                'USWest4',
                'USWest3',
                'USWest',
                'USSouthWest',
                'USSouth3',
                'USSouth',
                'USNorthWest',
                'USMidWest2',
                'USMidWest',
                'USEast2',
                'EUWest2',
                'EUSouthWest',
                'EUNorth',
                'EUEast',
                'Australia',
                'Asia'
            ]
        }
    )

    df_untracked_servers = df_all_servers[
        (
            df_all_servers['server'].apply(
                lambda server: server not in df['server'].unique()
            )
        )
    ].sort_values(
        by=['server'],
        ascending=True
    )
    

    df_tier_1 = df[
        (
            df['n_events_rem'] > 0
        ) & (
            df['n_events_rem'] <= 15
        )
    ].copy()

    df_tier_2 = df[
        (
            df['n_events_rem'] > 15
        ) & (
            df['n_events_rem'] <= 25
        )
    ].copy()


    df_tier_1_feasibility = calculate_realm_feasibility(df=df_tier_1)
    df_tier_2_feasibility = calculate_realm_feasibility(df=df_tier_2)
    df_potential_runs = calculate_potential_runs(df=df_tier_1)
    df_tier_2_feasibility = tier_2_deduplication(
        df_tier_1=df_tier_1_feasibility,
        df_tier_2=df_tier_2_feasibility
    )

    return df_tier_1_feasibility, df_tier_2_feasibility, df_potential_runs, df_untracked_servers, df_nexus


