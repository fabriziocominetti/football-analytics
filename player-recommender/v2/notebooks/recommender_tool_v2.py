### IMPORTS

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import math
import matplotlib.pyplot as plt
from bing_image_urls import bing_image_urls # bing library for automation image
from emoji_mapping import nation_to_emoji # add emoji for nation

### DATA

aggregated_2021_2024_90 = pd.read_csv("./player-recommender/v2/data/aggregated_2021_2024_90.csv")
num_cols_aggregated_2021_2024_90 = aggregated_2021_2024_90.select_dtypes(include='number')
features = num_cols_aggregated_2021_2024_90.columns.tolist()

# normalize the performance data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(num_cols_aggregated_2021_2024_90)

# apply PCA
pca = PCA(n_components=0.95)  # Retain 95% of variance
X_pca = pca.fit_transform(X_scaled)

def find_similar_players(player_name, pca_data, player_data, features, selected_nation, selected_league, selected_position):
    player_index = player_data[player_data['Player'] == player_name].index.tolist()[0]
    similarities = cosine_similarity([pca_data[player_index]], pca_data)[0]
    similar_players_indices = similarities.argsort()[::-1][1:]  # Exclude the player itself
    similar_players = player_data.iloc[similar_players_indices][['Player', 'Nation', 'League', 'Squad', 'Age', 'Position']]
    similar_players['similarity_score'] = similarities[similar_players_indices]
    if selected_nation:
        similar_players = similar_players[similar_players['Nation'].isin(selected_nation)]
    if selected_league:
        similar_players = similar_players[similar_players['League'].isin(selected_league)]
    if selected_position:
        similar_players = similar_players[similar_players['Position'] == selected_position]
    return similar_players

### STREAMLIT APP

st.title("Player Recommender Tool ⚽")
st.markdown("The Player Recommender Tool leverages data-driven insights to assist scouts, coaches, and analysts in making informed decisions during player recruitment and talent identification processes. This user-friendly interface allows you to explore player data and identify potential targets for scouting. It displays key metrics for the selected player and showcases similar players based on the applied filters. The ranking is determined through a model based on cosine similarity, and the data via FBRef refers to the 2021/2022, 2022/2023, and 2023/2024 seasons of the Top 5 leagues.")
st.markdown("The data, and thus the metrics, are aggregated by player and calculated as the average of the three seasons for which data were downloaded (2021/22, 2022/23, and 2023/24) and scaled based on 90-minute performances.")

# sidebar for filters
st.sidebar.title("🔎 Filters")

# dropdown menu for player selection
selected_player = st.sidebar.selectbox("Select a player", aggregated_2021_2024_90['Player'].unique())

# filter for age
min_age, max_age = int(aggregated_2021_2024_90['Age'].min()), int(aggregated_2021_2024_90['Age'].max())
selected_age = st.sidebar.slider("Select age range", min_age, max_age, (min_age, max_age))
# filter for nation
selected_nation = st.sidebar.multiselect("Select nation", aggregated_2021_2024_90['Nation'].unique())
# filter for league
selected_league = st.sidebar.multiselect("Select league", aggregated_2021_2024_90['League'].unique())

# display selected player details
st.header(f"Details of {selected_player}")
selected_player_data = aggregated_2021_2024_90[aggregated_2021_2024_90['Player'] == selected_player].set_index('Player')
st.write(selected_player_data)

# fetching player's squad
player_squad = selected_player_data['Squad'].iloc[0]
# fetching player's image URL
url_player = bing_image_urls(selected_player + " " + player_squad + " 2023", limit=1)[0]
url_squad = bing_image_urls(player_squad + "logo wikipedia", limit=1)[0]
# get the nation code of the selected player and the corresponding emoji for the nation code
nation_code = selected_player_data['Nation'][0]
emoji = nation_to_emoji.get(nation_code, nation_code)

# create a grid layout for player bio
col1, col2 = st.columns([2, 3])  # adjust column ratios as needed

with col1:
    st.image(url_player, caption=f"{selected_player}{','} {int(selected_player_data['Age'].iloc[0])}", width=250)

# calculate int stats
minutes_per_match = selected_player_data['Playing Time Min'].iloc[0] / selected_player_data['Playing Time MP'].iloc[0]
goals_scored = selected_player_data['Goals'].iloc[0] * selected_player_data['Playing Time 90s'].iloc[0]
assists = selected_player_data['Assists'].iloc[0] * selected_player_data['Playing Time 90s'].iloc[0]
yellow_cards = selected_player_data['Yellow Cards'].iloc[0] * selected_player_data['Playing Time 90s'].iloc[0]
red_cards = selected_player_data['Red Cards'].iloc[0] * selected_player_data['Playing Time 90s'].iloc[0]

with col2:
    # create sub-columns
    subcol1, subcol2, subcol3 = st.columns(3)
    with subcol1:
        st.metric("Nation", emoji)
        st.metric("Position", selected_player_data['Position'].iloc[0])
        st.markdown(f":gray[{selected_player_data['Squad'].iloc[0]}]")
        st.markdown(f":gray[{selected_player_data['League'].iloc[0]}]")
    with subcol2:
        st.metric("Matches Played", round(selected_player_data['Playing Time MP'], 2).iloc[0], help="Mean value across the last three seasons")
        st.metric("Goals", math.ceil(goals_scored), help=None)
        st.metric("Yellow Cards", math.ceil(yellow_cards), help=None)
    with subcol3:
        st.metric("Minutes per Match", round(minutes_per_match, 2), help=None)
        st.metric("Assists", math.ceil(assists), help=None)
        st.metric("Red Cards", math.ceil(red_cards), help=None)

# filtered similar players
similar_players = find_similar_players(selected_player, X_pca, aggregated_2021_2024_90, features, selected_nation, selected_league, selected_player_data['Position'].iloc[0])
similar_players_filtered = similar_players[(similar_players['Age'] >= selected_age[0]) & (similar_players['Age'] <= selected_age[1])]

# display similar players
if similar_players_filtered.empty:
    st.write(f"No similar players found in the selected age range {selected_age}.")
else:
    st.write(f"Similar players to {selected_player} in the age range {selected_age}")

    # display the first five similar players
    similar_players_first_five = similar_players_filtered.head(5).set_index('Player', drop=True)
    st.write(similar_players_first_five)

    # add a button to expand and view the rest of the table
    if len(similar_players_filtered) > 5:
        if st.button("Show more similar players"):
            similar_players_rest = similar_players_filtered.iloc[5:].set_index('Player', drop=True)
            st.write(similar_players_rest)

### TABLE COMPARISON

# dropdown to select a player to compare
player_to_compare = st.selectbox("Select a player to compare", similar_players_filtered['Player'].values)

# define the metrics dictionary for different positions
metrics_dict = {
    'FW': ['Playing Time MP', 'Goals', 'Assists', 'Penalty Goals', 'xG', 'Non-Penalty xG', 'xAG', 'Key Passes', 'Passes Penalty Area', 'Touches'],
    'MD': ['Playing Time MP', 'Goals', 'Assists', 'npxG+xAG', 'Tackles + Interceptions', 'Progressive Carries', 'Ball Recoveries', 'Pass Completion %', 'Key Passes', 'Touches'],
    'DF': ['Playing Time MP', 'Goals', 'Assists', 'Tackles Won', 'Errors', 'Clearances', 'Fouls Committed', 'Crosses', 'Aerial Duels Won%', 'Carries'],
    'GK': ['Playing Time MP', 'Touches', 'Goals Against', 'Shots on Target Against', 'Saves', 'Save %', 'Clean Sheets', 'Clean Sheet %', 'Penalty Kicks Saved', 'Penalty Kicks Save %']
}

# get position of the selected player
player_position = selected_player_data['Position'].iloc[0]

# get the relevant metrics based on the player's position
metrics = metrics_dict.get(player_position, [])

# extract the metrics for the selected player and round to two decimal places
selected_player_metrics = selected_player_data[metrics].iloc[0].fillna(0).round(2).values

# retrieve the row corresponding to the selected comparison player from the original dataset
comparison_player_data = aggregated_2021_2024_90[aggregated_2021_2024_90['Player'] == player_to_compare].iloc[0]

# extract the metrics for the comparison player and round to two decimal places
comparison_player_metrics = comparison_player_data[metrics].fillna(0).round(2).values

# create a DataFrame for comparison
comparison_df = pd.DataFrame({
    'Metric': metrics,
    selected_player: selected_player_metrics,
    player_to_compare: comparison_player_metrics
})

# define a function to highlight the better player for each metric
def highlight_better(row):
    player1 = row[selected_player]
    player2 = row[player_to_compare]
    if pd.isna(player1) or pd.isna(player2):
        return ['', '']
    if player1 > player2:
        return ['background-color: darkgreen', '']
    elif player2 > player1:
        return ['', 'background-color: darkgreen']
    else:
        return ['', '']

# apply the highlighting function to the DataFrame and set float format to two decimal places
comparison_df = comparison_df.style.apply(highlight_better, axis=1, subset=[selected_player, player_to_compare]).format("{:.2f}", subset=pd.IndexSlice[:, [selected_player, player_to_compare]])

# convert the DataFrame to HTML without the index and hide the left index column
comparison_html = comparison_df.to_html(index=False)

# display the comparison table without the index using markdown
st.markdown(comparison_html, unsafe_allow_html=True)
