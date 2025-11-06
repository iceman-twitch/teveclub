"""
Views for the Teveclub Bot API
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import sys
import os

# Add parent directory to path to import bot modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

print(f"[DEBUG] Parent directory: {parent_dir}")
print(f"[DEBUG] sys.path: {sys.path[:3]}")

try:
    from src.bot_core import TeveClub
    print("[DEBUG] TeveClub imported successfully")
except ImportError as e:
    # Fallback error handling
    print(f"[ERROR] Failed to import TeveClub: {e}")
    TeveClub = None
    import_error = str(e)


# Store active sessions (in production, use Django sessions or Redis)
active_sessions = {}


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """
    Handle login request
    POST /api/login/
    Body: {username: str, password: str}
    """
    print(f"[DEBUG] Login endpoint called")
    print(f"[DEBUG] Request method: {request.method}")
    print(f"[DEBUG] Request body: {request.body[:200]}")
    
    try:
        if TeveClub is None:
            error_msg = f'Bot module import error: {import_error}'
            print(f"[ERROR] {error_msg}")
            return JsonResponse({
                'success': False,
                'message': error_msg
            }, status=500)
        
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        print(f"[DEBUG] Username: {username}, Password: {'*' * len(password) if password else 'None'}")
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'message': 'Username and password are required'
            }, status=400)
        
        # Create bot instance
        print(f"[DEBUG] Creating TeveClub instance...")
        bot = TeveClub(username, password)
        
        # Try to login
        print(f"[DEBUG] Attempting login...")
        if bot.login():
            print(f"[DEBUG] Login successful!")
            # Store session
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            
            active_sessions[session_id] = bot
            print(f"[DEBUG] Session stored: {session_id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'session_id': session_id
            })
        else:
            print(f"[DEBUG] Login failed - invalid credentials")
            return JsonResponse({
                'success': False,
                'message': 'Invalid credentials'
            }, status=401)
            
    except Exception as e:
        print(f"[ERROR] Exception in login: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def feed(request):
    """
    Feed the pet
    POST /api/feed/
    """
    try:
        session_id = request.session.session_key
        
        if not session_id or session_id not in active_sessions:
            return JsonResponse({
                'success': False,
                'message': 'Not logged in'
            }, status=401)
        
        bot = active_sessions[session_id]
        
        # Get the page first to check feeding status
        r = bot.session.get('https://teveclub.hu/myTeve.php')
        
        if 'Mehet!' not in r.text:
            return JsonResponse({
                'success': True,
                'message': '✅ Pet is already well-fed! No feeding needed.'
            })
        
        success = bot.feed()
        
        return JsonResponse({
            'success': success,
            'message': '✅ Pet fed successfully!' if success else '❌ Feeding failed - please try again'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def learn(request):
    """
    Learn a new trick
    POST /api/learn/
    """
    try:
        session_id = request.session.session_key
        
        if not session_id or session_id not in active_sessions:
            return JsonResponse({
                'success': False,
                'message': 'Not logged in'
            }, status=401)
        
        bot = active_sessions[session_id]
        success = bot.learn()
        
        return JsonResponse({
            'success': success,
            'message': 'Learning successful' if success else 'No more tricks to learn'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def guess_game(request):
    """
    Play the guess game
    POST /api/guess/
    """
    try:
        session_id = request.session.session_key
        
        if not session_id or session_id not in active_sessions:
            return JsonResponse({
                'success': False,
                'message': 'Not logged in'
            }, status=401)
        
        bot = active_sessions[session_id]
        success = bot.guess()
        
        return JsonResponse({
            'success': success,
            'message': 'Guess game completed' if success else 'Guess game failed'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def logout(request):
    """
    Logout and clear session
    POST /api/logout/
    """
    try:
        session_id = request.session.session_key
        
        if session_id and session_id in active_sessions:
            del active_sessions[session_id]
        
        request.session.flush()
        
        return JsonResponse({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


def index(request):
    """
    Render the main page
    """
    from django.shortcuts import render
    return render(request, 'index.html')
