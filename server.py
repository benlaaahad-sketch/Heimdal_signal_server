# server.py - Signal Server ساده و پایدار برای Railway
from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60)

# دیکشنری کاربران آنلاین
online_users = {}

@app.route('/')
def index():
    return jsonify({
        "name": "Heimdal Signal Server",
        "version": "1.0",
        "online": len(online_users),
        "status": "running"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "online": len(online_users),
        "time": time.time()
    })

@socketio.on('connect')
def handle_connect():
    print(f"🟢 کاربر متصل شد: {request.sid}")

@socketio.on('register')
def handle_register(data):
    user_id = data.get('userId')
    city = data.get('city', 'unknown')
    
    if user_id:
        online_users[user_id] = {
            'sid': request.sid,
            'city': city,
            'joined': time.time()
        }
        
        emit('registered', {
            'status': 'ok',
            'online': len(online_users)
        })
        
        print(f"✅ کاربر {user_id} از {city} متصل شد")

@socketio.on('find_peer')
def handle_find_peer(data):
    city = data.get('city')
    exclude = data.get('exclude', [])
    
    candidates = []
    for uid, info in online_users.items():
        if info['city'] == city and uid not in exclude and info['sid'] != request.sid:
            candidates.append({
                'userId': uid,
                'sid': info['sid']
            })
    
    if candidates:
        import random
        peer = random.choice(candidates)
        emit('peer_found', {
            'peerId': peer['userId'],
            'sid': peer['sid']
        }, room=request.sid)
    else:
        emit('peer_found', {
            'peerId': None,
            'message': 'هم‌شهری پیدا نشد'
        }, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    for uid, info in list(online_users.items()):
        if info['sid'] == request.sid:
            del online_users[uid]
            print(f"🔴 کاربر {uid} قطع شد")
            break

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
