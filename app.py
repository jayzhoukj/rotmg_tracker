import asyncio

import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer

from src.pipeline import (
    webscraping_pipeline,
    data_processing_pipeline
)


# Setup page headers
st.set_page_config(
    page_title='ROTMG Events Tracker',
    layout='wide'
)


# Getting data
df_raw, data_collected_time = webscraping_pipeline()
df_tier_1, df_tier_2, df_potential_runs, df_untracked = data_processing_pipeline(df=df_raw)

data_collected_time_clean = data_collected_time.rsplit('.', 1)[0]


# App page
st.title('ROTMG Events Tracker')
st.write(f'Data last refreshed on {data_collected_time_clean} GMT+00:00')

left_panel, right_panel = st.columns(2)

with left_panel:
    st.subheader('Tier 1 Locations for O3 runs')

    st.dataframe(
        data=df_tier_1,
        use_container_width=True,
        hide_index=True
    )

    st.subheader('Tier 2 Locations for O3 runs')

    st.dataframe(
        data=df_tier_2,
        use_container_width=True,
        hide_index=True
    )


with right_panel:
    st.subheader('Potential O3 Runs')

    st.dataframe(
        data=df_potential_runs,
        use_container_width=True,
        hide_index=True
    )

    st.subheader('Untracked Servers')

    st.dataframe(
        data=df_untracked,
        use_container_width=True,
        hide_index=True
    )


# async def watch(refresh_label, table1, table2):
#     while True:
#         # Getting data
#         df_raw, data_collected_time = webscraping_pipeline()
#         df = data_processing_pipeline(df=df_raw) 

#         data_collected_time_clean = data_collected_time.rsplit('.', 1)[0]
        
#         refresh_label.write(f'Data last refreshed on {data_collected_time_clean}')

#         table1.dataframe(
#             data=df,
#             use_container_width=True,
#             hide_index=True
#         )

#         table2.dataframe(
#             data=df.drop(
#                 columns=['score']
#             ).sort_values(
#                 by=[
#                     'n_players',
#                     'n_events_rem'
#                 ],
#                 ascending=[
#                     False,
#                     True
#                 ]
#             ),
#             use_container_width=True,
#             hide_index=True
#         )

#         r = await asyncio.sleep(0.001)

# asyncio.run(
#     watch(
#         refresh_label=refresh_label,
#         table1=table1,
#         table2=table2
#     )
# )

