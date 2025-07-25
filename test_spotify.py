# test_spotify.py
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

st.title("Spotify API Audio Features Test")
st.write("This app tests if your API credentials have permission to access the `audio_features` endpoint.")

# --- Load Credentials ---
try:
    client_id = st.secrets["CLIENT_ID"]
    client_secret = st.secrets["CLIENT_SECRET"]
    st.success("✅ Successfully loaded credentials from secrets.toml.")
except Exception as e:
    st.error(f"Could not load credentials. Make sure your .streamlit/secrets.toml file is correct. Error: {e}")
    st.stop()

# --- Create Spotify Client ---
try:
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    st.success("✅ Spotify client created successfully.")
except Exception as e:
    st.error(f"Could not create Spotify client. Error: {e}")
    st.stop()

# --- Hardcoded Track ID for "Shape of You" ---
track_id = '7qiZfU4dY1lWllzX7mP3AU'
st.info(f"Attempting to fetch audio features for track ID: {track_id}")

# --- The Test ---
try:
    features = sp.audio_features([track_id])
    st.success("🎉 API call successful!")
    st.write("Spotify returned the following data:")
    st.json(features)
except Exception as e:
    st.error("❌ API call FAILED.")
    st.write("This is the error that is causing your main app to fail. It is likely a permissions issue with your Spotify Developer account.")
    st.exception(e)