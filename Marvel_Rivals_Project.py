import streamlit as st
import requests
import pandas as pd

API_KEY = 'add API key here'
HEADERS = {'x-api-key': API_KEY}

def update_player_data(username):
    url = f'https://marvelrivalsapi.com/api/v1/player/{username}/update'
    return requests.get(url, headers=HEADERS)

def get_player_stats(username):
    url = f'https://marvelrivalsapi.com/api/v1/player/{username}'
    return requests.get(url, headers=HEADERS)

st.set_page_config(page_title="Marvel Rivals Tracker", layout="wide")
st.title('Marvel Rivals Player Stats')

with st.sidebar:
    st.header("Player Selection")
    player_name = st.text_input("Enter a player's username:")

    if st.button("Refresh Stats"):
        if player_name:
            st.info("Requesting data update...")
            update_response = update_player_data(player_name)
            if update_response.status_code == 200:
                st.success("Player data updated!")
            else:
                st.warning(f"Failed to update data: {update_response.status_code}")
        else:
            st.warning("Please enter a player username above to refresh stats.")

if player_name:
    st.info('Fetching player stats...')
    response = get_player_stats(player_name)

    if response.status_code == 200:
        data = response.json()
        st.subheader(f'Stats for {player_name}')

        ranked_stats = data.get('overall_stats', {}).get('ranked', {})
        total_matches = ranked_stats.get('total_matches', 0)
        total_wins = ranked_stats.get('total_wins', 0)
        win_rate = (total_wins / total_matches) * 100 if total_matches > 0 else 0
        current_rank = data.get("player", {}).get("rank", {}).get("rank", "N/A")

        st.markdown("Ranked Game Summary")
        st.markdown(f"- Current Rank: {current_rank}")
        st.markdown(f"- Total Ranked Matches: {total_matches}")
        st.markdown(f"- Total Ranked Wins: {total_wins}")
        st.markdown(f"- Win Rate: {win_rate:.2f}%")

        heroes_ranked = data.get('heroes_ranked', [])
        hero_stats = []

        for hero in heroes_ranked:
            matches = hero.get('matches', 0)
            wins = hero.get('wins', 0)
            if matches > 0:
                hero_stats.append({
                    'Hero': hero['hero_name'],
                    'Matches Played': matches,
                    'Wins': wins,
                    'Win Rate (%)': round((wins / matches) * 100, 2)
                })

        if hero_stats:
            hero_df = pd.DataFrame(hero_stats).sort_values('Matches Played', ascending=False)
            top5_df = hero_df.head(5)

            st.subheader("Top 5 Ranked Heroes by Usage")
            st.dataframe(top5_df.drop(columns='Win Rate (%)'), use_container_width=True)
            st.bar_chart(top5_df.set_index("Hero")[["Matches Played", "Wins"]])
        else:
            st.warning("No ranked hero data available.")
    else:
        st.error(f"Failed to fetch data for {player_name}. Status Code: {response.status_code}")
else:
    st.warning("Please enter a player's username in the sidebar to view stats.")
