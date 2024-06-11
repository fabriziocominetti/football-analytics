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

### DATA

big5_def_90min = pd.read_csv("./player-recommender/v1/data/big5_def_90min.csv")
num_cols_90min = big5_def_90min.select_dtypes(include='number')
features = num_cols_90min.columns.tolist()

# normalize data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(num_cols_90min)

# apply PCA
pca = PCA(n_components=0.95)  # Retain 95% of variance
X_pca = pca.fit_transform(X_scaled)

# function to find similar players
def find_similar_players(player_name, pca_data, player_data, features, selected_nation, selected_league):
    player_index = player_data[player_data['Player'] == player_name].index.tolist()[0]
    similarities = cosine_similarity([pca_data[player_index]], pca_data)[0]
    similar_players_indices = similarities.argsort()[::-1][1:]  # Exclude the player itself
    similar_players = player_data.iloc[similar_players_indices][['Player', 'Nation', 'League', 'Squad', 'Age']]
    similar_players['similarity_score'] = similarities[similar_players_indices]
    if selected_nation:
        similar_players = similar_players[similar_players['Nation'].isin(selected_nation)]
    if selected_league:
        similar_players = similar_players[similar_players['League'].isin(selected_league)]
    return similar_players

### STREAMLIT APP

st.title("Player Recommender Tool ⚽")
st.markdown("The Player Recommender Tool leverages data-driven insights to assist scouts, coaches, and analysts in making informed decisions during player recruitment and talent identification processes. This user-friendly interface allows you to explore player data and identify potential targets for scouting. It displays key metrics for the selected player and showcases similar players based on the applied filters. The ranking is determined through the application of a model based on cosine similarity, and the data refers to the 2023/2024 season of the Top 5 leagues, scaled based on 90-minute performances.")

# sidebar for filters
st.sidebar.title("🔎 Filters")

# dropdown menu for player selection
selected_player = st.sidebar.selectbox("Select a player", big5_def_90min['Player'].unique())

# filter for age
min_age, max_age = int(big5_def_90min['Age'].min()), int(big5_def_90min['Age'].max())
selected_age = st.sidebar.slider("Select age range", min_age, max_age, (min_age, max_age))
# filter for nation
selected_nation = st.sidebar.multiselect("Select nation", big5_def_90min['Nation'].unique())
# filter for league
selected_league = st.sidebar.multiselect("Select league", big5_def_90min['League'].unique())

# display selected player details
st.header(f"Details of {selected_player}")
selected_player_data = big5_def_90min[big5_def_90min['Player'] == selected_player].set_index('Player')
st.write(selected_player_data)

# fetching player's squad
player_squad = selected_player_data['Squad'].iloc[0]
# fetching player's image URL
url_player = bing_image_urls(selected_player + " " + player_squad + " 2023", limit=1)[0]
url_squad = bing_image_urls(player_squad + "logo wikipedia", limit=1)[0]

# create a grid layout for player bio
col1, col2, col3 = st.columns([3, 2, 3])  # adjust column ratios as needed

# displaying player's image in the first column
with col1:
    st.image(url_player, caption=selected_player, width=250)

# displaying player's bio in the second column
with col2:
    st.markdown(f"**{selected_player_data['Squad'].iloc[0]}**")
    st.markdown(f"**{selected_player_data['League'].iloc[0]}**")
    st.markdown(f"**{selected_player_data['Nation'].iloc[0]}**")
    st.markdown(f"**{selected_player_data['Age'].iloc[0]}**")
    st.markdown(f"**{selected_player_data['Position'].iloc[0]}**")

# calculate int stats
minutes_per_match = selected_player_data['Playing Time Min'].iloc[0] / selected_player_data['Playing Time MP'].iloc[0]
goals_scored = selected_player_data['Goals'].iloc[0] * selected_player_data['Playing Time 90s'].iloc[0]
assists = selected_player_data['Assists'].iloc[0] * selected_player_data['Playing Time 90s'].iloc[0]
yellow_cards = selected_player_data['Yellow Cards'].iloc[0] * selected_player_data['Playing Time 90s'].iloc[0]
red_cards = selected_player_data['Red Cards'].iloc[0] * selected_player_data['Playing Time 90s'].iloc[0]

# displaying player's metrics in the third column
with col3:
    # create sub-columns
    subcol1, subcol2 = st.columns(2)
    # display metrics in the left sub-column
    with subcol1:
        st.metric("Matches Played", selected_player_data['Playing Time MP'].iloc[0], help=None)
        st.metric("Goals", math.ceil(goals_scored), help=None)
        st.metric("Yellow Cards", math.ceil(yellow_cards), help=None)
    # display metrics in the right sub-column
    with subcol2:
        st.metric("Minutes per Match", round(minutes_per_match, 2), help=None)
        st.metric("Assists", math.ceil(assists), help=None)
        st.metric("Red Cards", math.ceil(red_cards), help=None)

# filtered similar players
similar_players = find_similar_players(selected_player, X_pca, big5_def_90min, features, selected_nation, selected_league)
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

# define the metrics to compare
metrics = ['Goals', 'Assists', 'Penalty Goals', 'xG', 'Non-Penalty xG', 'xAG', 'Progressive Carries', 'Progressive Passes', 'Progressive Passes Received']

# extract the metrics for the selected player and round to two decimal places
selected_player_metrics = selected_player_data[metrics].iloc[0].fillna(0).round(2).values

# retrieve the row corresponding to the selected comparison player from the original dataset
comparison_player_data = big5_def_90min[big5_def_90min['Player'] == player_to_compare].iloc[0]

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

# convert the DataFrame to HTML without the index
comparison_html = comparison_df.to_html(index=False)

# display the comparison table without the index using markdown
st.markdown(comparison_html, unsafe_allow_html=True)