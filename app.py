from flask import Flask, request, jsonify
import requests
import json
from google.generativeai import client, types
import firebase_admin
from firebase_admin import credentials, db

# Flask 앱 초기화
app = Flask(__name__)

# Firebase 초기화
cred = credentials.Certificate('your-firebase-service-account-key.json')  # Firebase 서비스 계정 키
firebase_admin.initialize_app(cred, {'databaseURL': 'https://your-firebase-url.firebaseio.com/'})
db = firebase_admin.db

# Spotify API 연동
def get_spotify_analysis(music_title, singer_name):
    # Spotify에서 음악 정보 검색
    headers = {
        'Authorization': 'Bearer your_spotify_api_token'  # Spotify OAuth 토큰을 추가해야 해
    }
    spotify_response = requests.get(f'https://api.spotify.com/v1/search?q=track:{music_title} artist:{singer_name}&type=track', headers=headers)
    return spotify_response.json()

# 구글 AI 모델을 통한 향수 추천 함수
def get_perfume_recommendation(song_title, note_info):
    filepath = pathlib.Path('fra_cleaned.tab2.csv')

    prompt = f"이 문서를 읽고 '{song_title}' 라는 노래에 어울리는 향수 조합을 추천해줘. {note_info}"
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[types.Part.from_bytes(data=filepath.read_bytes(), mime_type='text/csv'), prompt]
    )
    return response.text

# 향수 추천 데이터를 Firebase에 저장하는 함수
def save_fragrance_data(song_title, fragrance_data):
    ref = db.reference(f'/fragrance_recommendations/{song_title}')
    ref.set(fragrance_data)

@app.route('/get_perfume', methods=['POST'])
def get_perfume():
    data = request.get_json()
    music_title = data['music_title']
    singer_name = data['singer_name']

    # Spotify API로 음악 정보 검색
    spotify_data = get_spotify_analysis(music_title, singer_name)
    song_info = spotify_data['tracks']['items'][0]
    song_title = song_info['name']
    
    # 향수 추천 (구글 AI)
    note_info = "향수 노트 정보"  # 향수 정보 제공 (실제 데이터를 바탕으로)
    fragrance_data = get_perfume_recommendation(song_title, note_info)

    # 향수 추천 데이터를 Firebase에 저장
    save_fragrance_data(song_title, fragrance_data)

    return jsonify({'perfume_name': fragrance_data})

if __name__ == '__main__':
    app.run(debug=True)
