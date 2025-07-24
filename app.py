import streamlit as st
import pandas as pd
import joblib


@st.cache_resource
def load_model():
    model = joblib.load('trained_model.joblib')
    return model

@st.cache_resource
def load_scaler():
    scaler = joblib.load('scaler.joblib')
    return scaler

model = load_model()
scaler = load_scaler()


st.title('🎵 Music Popularity Predictor')
st.write("This app predicts whether a song will be popular based on its audio features. Adjust the sliders below to see the prediction!")

st.sidebar.header('Song Features')


def user_input_features():
    danceability = st.sidebar.slider('Danceability', 0.0, 1.0, 0.5)
    energy = st.sidebar.slider('Energy', 0.0, 1.0, 0.5)
    loudness = st.sidebar.slider('Loudness (dB)', -60.0, 0.0, -5.0)
    speechiness = st.sidebar.slider('Speechiness', 0.0, 1.0, 0.1)
    acousticness = st.sidebar.slider('Acousticness', 0.0, 1.0, 0.2)
    instrumentalness = st.sidebar.slider('Instrumentalness', 0.0, 1.0, 0.0)
    liveness = st.sidebar.slider('Liveness', 0.0, 1.0, 0.2)
    valence = st.sidebar.slider('Valence', 0.0, 1.0, 0.5)
    tempo = st.sidebar.slider('Tempo (BPM)', 0.0, 250.0, 120.0)
    duration_ms = st.sidebar.slider('Duration (ms)', 0, 1000000, 200000)

    data = {
        'acousticness': acousticness,
        'danceability': danceability,
        'duration_ms': duration_ms,
        'energy': energy,
        'instrumentalness': instrumentalness,
        'liveness': liveness,
        'loudness': loudness,
        'speechiness': speechiness,
        'tempo': tempo,
        'valence': valence
    }
    features = pd.DataFrame(data, index=[0])
    return features

input_df = user_input_features()


st.subheader('Your Song\'s Features:')
st.write(input_df)

if st.button('Predict Popularity'):
    
    input_scaled = scaler.transform(input_df)
    
   
    prediction = model.predict(input_scaled)
    prediction_proba = model.predict_proba(input_scaled)

    st.subheader('Prediction')
    if prediction[0] == 1:
        st.success('This song is likely to be **Popular**! 👍')
    else:
        st.error('This song is likely to be **Not Popular**. 👎')

    st.write('Prediction Probability:')
    st.write(f"Not Popular: {prediction_proba[0][0]:.2f}")
    st.write(f"Popular: {prediction_proba[0][1]:.2f}")
