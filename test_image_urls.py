import requests

urls = [
    'https://images.unsplash.com/photo-1617469767537-b85d00004b58?w=800&h=600&fit=crop&auto=format',
]

for url in urls:
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        print(f'✓ URL accessible: {response.status_code}')
    except Exception as e:
        print(f'✗ URL error: {e}')
