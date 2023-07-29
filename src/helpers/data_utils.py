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

    df = df.drop(
        columns=[
            'status',
            'rem_counts'
        ]
    )

    df_nexus = df[
        (
            df['realm'] == 'Nexus'
        )
    ]
    
    df = df[
        (
            df['realm'] != 'Nexus'
        ) & (
            df['server'] != 'EUWest'
        ) & (
            df['server'] != 'USEast'
        )
    ]

    return df, df_nexus


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
    df['n_events_rem'] = df['n_events_rem'].apply(int)
    df['n_players'] = df['n_players'].apply(int)

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

    df = df.sort_values(
        by=['n_events_rem'],
        ascending=True
    )

    df = df.drop_duplicates(
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
    
    df.sort_values(
        by=['score'],
        ascending=False,
        inplace=True
    )

    return df


def tier_2_deduplication(
    df_tier_1: pd.DataFrame,
    df_tier_2: pd.DataFrame
):
    # Deduplicate Tier 2 locations with Tier 1 locations
    df_tier_2 = df_tier_2[
        (
            df_tier_2['server'].apply(
                lambda server: server not in df_tier_1['server'].unique()
            )
        ) & (
            df_tier_2['realm'].apply(
                lambda realm: realm not in df_tier_1['realm'].unique()
            )
        )
    ]

    return df_tier_2


