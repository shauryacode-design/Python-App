import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import app as app_mod
app = getattr(app_mod, 'app')
client = app.test_client()
res = client.get('/property/1')
print('status', res.status_code)
html = res.get_data(as_text=True)
print('--- first 400 chars ---')
print(html[:400])
print('\n--- link/script tags found ---')
for line in html.split('\n'):
    if 'href=' in line or 'src=' in line:
        print(line.strip())
