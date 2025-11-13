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
import re
from bs4 import BeautifulSoup
from lxml import html as lxml_html


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


@csrf_exempt
@require_http_methods(["GET"])
def get_current_trick(request):
    """
    Fetch current trick text from myteve.pet
    Returns: {trick: str}
    """
    try:
        # Get persistent session
        session = get_session_for_user(request)
        
        # Fetch myteve.pet page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        response = session.get(
            'https://teveclub.hu/myteve.pet',
            headers=headers,
            timeout=30,
            verify=False
        )
        
        if response.status_code != 200:
            return JsonResponse({
                'success': False,
                'message': f'Failed to fetch myteve.pet: {response.status_code}'
            })
        
        # Parse HTML with lxml
        tree = lxml_html.fromstring(response.content)
        
        # Get trick text using xpath - try multiple possible paths
        trick_elements = tree.xpath('/html/body/center/table/tbody/tr[1]/td[2]/center/table[3]/tbody/tr/td/table/tbody/tr[3]/td[2]/div[1]')
        
        if not trick_elements:
            # Try without tbody (browsers auto-insert tbody but HTML might not have it)
            trick_elements = tree.xpath('/html/body/center/table/tr[1]/td[2]/center/table[3]/tr/td/table/tr[3]/td[2]/div[1]')
        
        if not trick_elements:
            # Try more flexible pattern looking for specific text
            trick_elements = tree.xpath('//div[contains(text(), "Tanult trükk") or contains(text(), "trükk")]')
        
        trick_text = None
        if trick_elements:
            # Get all text nodes before <br> tag
            div_element = trick_elements[0]
            text_parts = []
            
            # Iterate through text content and child elements
            if div_element.text:
                text_parts.append(div_element.text)
            
            for child in div_element:
                if child.tag == 'br':
                    break  # Stop at first <br>
                if child.text:
                    text_parts.append(child.text)
                if child.tail:
                    text_parts.append(child.tail)
            
            trick_text = ''.join(text_parts).strip()
            print(f"[GET_CURRENT_TRICK] Found trick: {trick_text}")
        else:
            # Debug output
            print("[GET_CURRENT_TRICK] Trick element not found, trying to find any table structure")
            tables = tree.xpath('//table')
            print(f"[GET_CURRENT_TRICK] Found {len(tables)} tables in HTML")
        
        return JsonResponse({
            'success': True,
            'trick': trick_text
        })
        
    except Exception as e:
        print(f"[GET_CURRENT_TRICK] Error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_current_food_drink(request):
    """
    Fetch and parse current food/drink from myteve.pet
    Returns: {foodId: int, foodIcon: str, drinkId: int, drinkIcon: str}
    """
    try:
        # Get persistent session
        session = get_session_for_user(request)
        
        # Fetch myteve.pet page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        response = session.get(
            'https://teveclub.hu/myteve.pet',
            headers=headers,
            timeout=30,
            verify=False
        )
        
        if response.status_code != 200:
            return JsonResponse({
                'success': False,
                'message': f'Failed to fetch myteve.pet: {response.status_code}'
            })
        
        html = response.text
        
        # Parse HTML to find food and drink images
        result = {
            'foodId': None,
            'foodIcon': None,
            'drinkId': None,
            'drinkIcon': None
        }
        
        # Look for food: "Etet\u0151" or "Eteto" followed by image
        # Try multiple patterns
        food_match = re.search(r'Etet[\u0151o][^<]*<[^>]*<a[^>]*>.*?files/(\d+)\.gif', html, re.IGNORECASE | re.DOTALL)
        if not food_match:
            food_match = re.search(r'Etet[\u0151o].*?(\d+)\.gif', html, re.IGNORECASE | re.DOTALL)
        if not food_match:
            # Try simpler pattern matching any path before number.gif
            food_match = re.search(r'Etet[\u0151o].*?/(\d+)\.gif', html, re.IGNORECASE | re.DOTALL)
        
        if food_match:
            result['foodId'] = int(food_match.group(1))
            result['foodIcon'] = f"{food_match.group(1)}.gif"
            print(f"[GET_FOOD_DRINK] Found food: {result['foodId']}")
        else:
            # Debug: show what we're searching in
            food_section = re.search(r'Etet[\u0151o].{0,200}', html, re.IGNORECASE | re.DOTALL)
            if food_section:
                print(f"[GET_FOOD_DRINK] Food section sample: {food_section.group(0)}")
            else:
                print("[GET_FOOD_DRINK] Food keyword not found in HTML")
        
        # Look for drink: "Itat\u00f3" or "Itato" followed by image
        drink_match = re.search(r'Itat[\u00f3o][^<]*<[^>]*<a[^>]*>.*?files/(\d+)\.gif', html, re.IGNORECASE | re.DOTALL)
        if not drink_match:
            drink_match = re.search(r'Itat[\u00f3o].*?(\d+)\.gif', html, re.IGNORECASE | re.DOTALL)
        if not drink_match:
            drink_match = re.search(r'Itat[\u00f3o].*?/(\d+)\.gif', html, re.IGNORECASE | re.DOTALL)
            
        if drink_match:
            result['drinkId'] = int(drink_match.group(1))
            result['drinkIcon'] = f"{drink_match.group(1)}.gif"
            print(f"[GET_FOOD_DRINK] Found drink: {result['drinkId']}")
        else:
            # Debug: show what we're searching in
            drink_section = re.search(r'Itat[\u00f3o].{0,200}', html, re.IGNORECASE | re.DOTALL)
            if drink_section:
                print(f"[GET_FOOD_DRINK] Drink section sample: {drink_section.group(0)}")
            else:
                print("[GET_FOOD_DRINK] Drink keyword not found in HTML")
        
        return JsonResponse({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        print(f"[GET_FOOD_DRINK] Error: {e}")
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
