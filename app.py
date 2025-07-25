# app.py (Final Working Version)

import streamlit as st
import pandas as pd
import joblib
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
import re

# --- Load Model and Scaler ---
@st.cache_resource
def load_model():
    try:
        model = joblib.load('trained_model.joblib')
        return model
    except Exception:
        return None

@st.cache_resource
def load_scaler():
    try:
        scaler = joblib.load('scaler.joblib')
        return scaler
    except Exception:
        return None

model = load_model()
scaler = load_scaler()

# --- Spotify API Setup ---
@st.cache_resource
def get_spotify_client():
    try:
        if "CLIENT_ID" not in st.secrets or "CLIENT_SECRET" not in st.secrets:
            st.error("Spotify credentials are not configured.")
            return None
        client_credentials_manager = SpotifyClientCredentials(client_id=st.secrets["CLIENT_ID"], client_secret=st.secrets["CLIENT_SECRET"])
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=20, retries=3)
        sp.search(q="test", type='track', limit=1)
        return sp
    except Exception as e:
        st.error(f"Could not connect to Spotify. Error: {e}")
        return None

sp = get_spotify_client()

# --- Helper Functions ---
def sanitize_search_query(query):
    query = re.sub(r'[^\w\s\-]', '', query).strip()
    return query or "test"

def ensure_feature_order(df):
    correct_order = ['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence']
    return df[correct_order]

def search_and_analyze_song(song_name, spotify_client):
    if not song_name or not spotify_client: return None, None, None
    base = sanitize_search_query(song_name)
    queries = [ base, f'track:"{base}"' ]
    tracks_found = []
    for q in queries:
        try:
            res = spotify_client.search(q=q, type='track', limit=10, market='US')
            if res and res['tracks']['items']:
                tracks_found.extend(res['tracks']['items'])
        except Exception as e:
            continue
    if not tracks_found: return None, None, None
    uniq = {t['id']: t for t in tracks_found}
    candidate_tracks = list(uniq.values())[:5]
    needed = ['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence']
    for t in candidate_tracks:
        if not t.get('is_playable'): continue
        tid, tname, aname = t['id'], t['name'], t['artists'][0]['name']
        af = None
        try:
            features_list = spotify_client.audio_features([tid])
            if features_list and features_list[0]:
                af = features_list[0]
        except Exception:
            continue
        if not af: continue
        feats = {k: af.get(k) for k in needed if af.get(k) is not None}
        if len(feats) < 7: continue
        defaults = {'acousticness': 0.3, 'danceability': 0.6, 'duration_ms': 210000, 'energy': 0.6, 'instrumentalness': 0.05, 'liveness': 0.15, 'loudness': -8.0, 'speechiness': 0.05, 'tempo': 110, 'valence': 0.6}
        for k in needed: feats.setdefault(k, defaults[k])
        df = pd.DataFrame([feats])
        df = ensure_feature_order(df)
        return df, tname, aname
    return None, None, None

# --- App Interface ---
st.title('🎵 Music Popularity Predictor')
st.markdown("**Enter any song name to get its popularity prediction**")
song_input = st.text_input("🎤 Song Name:", placeholder="e.g., Shape of You, Blinding Lights, Tum Hi Ho")
if song_input:
    if sp:
        if not model or not scaler:
            st.error("❌ Prediction model not available.")
        else:
            with st.spinner('🔍 Searching and analyzing song...'):
                input_df, song_name, artist_name = search_and_analyze_song(song_input, sp)
            if input_df is not None and song_name and artist_name:
                try:
                    input_scaled = scaler.transform(input_df)
                    prediction_proba = model.predict_proba(input_scaled)
                    popularity_percentage = prediction_proba[0][1] * 100
                    st.markdown("---")
                    st.subheader(f"🎵 {song_name}")
                    st.write(f"**Artist:** {artist_name}")
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        st.metric(label="Popularity Score", value=f"{popularity_percentage:.1f}%")
                        if popularity_percentage >= 50: st.success("🎉 **POPULAR**")
                        else: st.error("📉 **NOT POPULAR**")
                    with col2:
                        st.write("**Popularity Level:**")
                        st.progress(min(popularity_percentage / 100, 1.0))
                        if popularity_percentage >= 75: st.write("🔥 **Highly Popular**")
                        elif popularity_percentage >= 50: st.write("⭐ **Popular**")
                        elif popularity_percentage >= 25: st.write("📊 **Moderate**")
                        else: st.write("📉 **Low Appeal**")
                    status = "POPULAR" if popularity_percentage >= 50 else "NOT POPULAR"
                    st.info(f"**'{song_name}' by {artist_name}** has a **{popularity_percentage:.1f}% popularity score** and is classified as **{status}**.")
                except Exception as e:
                    st.error("❌ Unable to make prediction.")
            else:
                st.warning(f"❌ Could not find '{song_input}' on Spotify.")
                st.info("💡 **Try including the artist name or check spelling**")
else:
    st.info("👆 **Enter a song name above to check its popularity!**")
    st.markdown("### 🎵 **Try these examples:**")
    col1, col2, col3 = st.columns(3)
    with col1: st.write("**English:**"); st.write("• Shape of You"); st.write("• Blinding Lights")
    with col2: st.write("**Hindi:**"); st.write("• Tum Hi Ho"); st.write("• Kal Ho Naa Ho")
    with col3: st.write("**Regional:**"); st.write("• Butta Bomma"); st.write("• Rowdy Baby")
st.markdown("---")
st.markdown("*🎶 Music Popularity Predictor*")