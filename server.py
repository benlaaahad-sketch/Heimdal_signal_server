# server.py - Signal Server برای پیدا کردن همدیگه
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import uuid
import time

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ذخیره در RAM (با ریستارت پاک میشه)
online_users = {}
online_count = 0

@app.route('/')
def index():
    return jsonify({
        "name": "Heimdal Signal Server",
        "version": "3.0",
        "online": len(online_users),
        "status": "running"
    })

@app.route('/stats')
def stats():
    return jsonify({
        "online": len(online_users),
        "users": list(online_users.keys())[:10],
        "time": time.time()
    })

@socketio.on('register')
def handle_register(data):
    """ثبت کاربر در شبکه"""
    global online_count
    
    user_id = data.get('userId')
    city = data.get('city', 'unknown')
    
    if user_id:
        online_users[user_id] = {
            'sid': request.sid,
            'city': city,
            'joined': time.time(),
            'user_agent': request.headers.get('User-Agent', 'unknown')
        }
        
        join_room(f"city_{city}")
        online_count = len(online_users)
        
        emit('registered', {
            'status': 'ok',
            'online': online_count
        })
        
        print(f"✅ کاربر {user_id} از {city} متصل شد - کل: {online_count}")

@socketio.on('find_peer')
def handle_find_peer(data):
    """پیدا کردن کاربر هم‌شهر"""
    city = data.get('city')
    exclude = data.get('exclude', [])
    
    candidates = []
    for uid, info in online_users.items():
        if info['city'] == city and uid not in exclude:
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
    """کاربر آفلاین شد"""
    for uid, info in list(online_users.items()):
        if info['sid'] == request.sid:
            del online_users[uid]
            print(f"🔴 کاربر {uid} قطع شد - مانده: {len(online_users)}")
            break

if __name__ == '__main__':
    print("🚀 Signal Server راه‌اندازی شد...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
