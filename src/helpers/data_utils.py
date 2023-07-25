import numpy as np
import pandas as pd


def extract_rem_count(text):
    if 'Events' in text:
        try:
            output = int(text.split('Events')[0].strip())

        except:
            output = np.nan

    else:
        output = np.nan

    return output


def data_cleaning(df: pd.DataFrame):
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

    df['n_events_rem'] = df['rem_counts'].apply(extract_rem_count)

    df = df[
        (
            df['realm'] != 'Nexus'
        ) & (
            df['server'] != 'EUWest'
        ) & (
            df['server'] != 'USEast'
        )
    ].drop(
        columns=[
            'status',
            'rem_counts'
        ]
    )

    return df


def calculate_realm_feasibility(df: pd.DataFrame):
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

    return df


def calculate_potential_runs(df: pd.DataFrame):
    # Set calculation parameters
    events_weight = 0.2
    players_weight = 0.8

    max_realm_events = 50
    max_realm_players = 85

    # Calculate score for ranking potential o3 runs
    df['score'] = (
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

    df.sort_values(
        by=['score'],
        ascending=False,
        inplace=True
    )

    return df


