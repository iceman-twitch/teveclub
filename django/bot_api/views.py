"""
Views for the Teveclub Frontend
Django acts as a minimal proxy to bypass CORS
No bot logic - just forwards HTTP requests to teveclub.hu
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
import json


# Store sessions per Django session
def get_session_for_user(request):
    """Get or create a requests.Session for this Django session"""
    if 'requests_session_cookies' not in request.session:
        request.session['requests_session_cookies'] = {}
    
    # Create a new requests session with stored cookies
    session = requests.Session()
    cookies = request.session.get('requests_session_cookies', {})
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    return session


def save_session_for_user(request, session):
    """Save requests.Session cookies to Django session"""
    request.session['requests_session_cookies'] = dict(session.cookies.items())
    request.session.modified = True


@csrf_exempt
@require_http_methods(["POST"])
def proxy(request):
    """
    Proxy all requests to teveclub.hu
    Maintains session cookies between requests
    """
    try:
        data = json.loads(request.body)
        url = data.get('url')
        method = data.get('method', 'GET').upper()
        form_data = data.get('data', {})
        
        if not url:
            return JsonResponse({
                'success': False,
                'message': 'URL is required'
            }, status=400)
        
        # Get persistent session
        session = get_session_for_user(request)
        
        # Add comprehensive headers to mimic real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'hu-HU,hu;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # Add referer for POST requests
        if method == 'POST':
            headers['Referer'] = 'https://teveclub.hu/'
            headers['Origin'] = 'https://teveclub.hu'
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        # Make request to teveclub.hu
        try:
            if method == 'POST':
                response = session.post(
                    url, 
                    data=form_data, 
                    headers=headers, 
                    timeout=30,
                    allow_redirects=True,
                    verify=True
                )
            else:
                response = session.get(
                    url, 
                    headers=headers, 
                    timeout=30,
                    allow_redirects=True,
                    verify=True
                )
        except requests.exceptions.SSLError as e:
            # Try without SSL verification if SSL fails
            print(f"[PROXY] SSL Error, retrying without verification: {e}")
            if method == 'POST':
                response = session.post(
                    url, 
                    data=form_data, 
                    headers=headers, 
                    timeout=30,
                    allow_redirects=True,
                    verify=False
                )
            else:
                response = session.get(
                    url, 
                    headers=headers, 
                    timeout=30,
                    allow_redirects=True,
                    verify=False
                )
        
        # Save session cookies
        save_session_for_user(request, session)
        
        # Debug: log response
        print(f"[PROXY] {method} {url}")
        print(f"[PROXY] Status: {response.status_code}")
        print(f"[PROXY] Response length: {len(response.text)} chars")
        print(f"[PROXY] Cookies: {dict(session.cookies.items())}")
        
        # Check if we got an error page
        if response.status_code >= 500:
            print(f"[PROXY] Server error response: {response.text[:200]}")
        
        return JsonResponse({
            'success': response.status_code < 400,
            'html': response.text,
            'status': response.status_code
        })
        
    except requests.exceptions.Timeout:
        print("[PROXY] Request timeout")
        return JsonResponse({
            'success': False,
            'message': 'Request timed out'
        }, status=504)
    except requests.exceptions.RequestException as e:
        print(f"[PROXY] Request exception: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Request failed: {str(e)}'
        }, status=500)
    except Exception as e:
        print(f"[PROXY] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


def index(request):
    """
    Render the main page
    Frontend JavaScript calls Django proxy which forwards to teveclub.hu
    """
    return render(request, 'index.html')
