"""
Hits every major URL as each demo role and flags any 500s (template or
view bugs). Run with:
  python manage.py shell -c "exec(open('scripts/coverage_check.py').read())"
"""
from django.test import Client
from django.test.utils import setup_test_environment

setup_test_environment()

URLS = [
    '/dashboard/',
    '/personnel/',
    '/personnel/add/',
    '/absence/',
    '/absence/due-to-return/',
    '/absence/add/',
    '/strength/',
    '/strength/summary/',
    '/strength/add/',
    '/duty/',
    '/duty/upcoming/',
    '/duty/add/',
    '/reports/',
    '/reports/personnel/',
    '/reports/personnel/export/',
    '/reports/strength/',
    '/reports/strength/export/',
    '/reports/absence/',
    '/reports/absence/export/',
    '/reports/duty/',
    '/reports/duty/export/',
    '/reports/due-to-return/',
    '/reports/due-to-return/export/',
    '/accounts/users/',
    '/accounts/users/add/',
    '/accounts/my-password/',
    '/admin/',
]

CREDS = {
    'superadmin': 'Sup3rAdmin!2024',
    'adjt_admin': 'AdjtAdmin!2024',
    'clerk_acoy': 'ClerkACoy!2024',
    'viewer1': 'Viewer1!2024',
}

errors = []
for username, password in CREDS.items():
    c = Client()
    login_resp = c.post('/login/', {'username': username, 'password': password})
    print(f"\n== {username} (login status {login_resp.status_code}) ==")
    for url in URLS:
        resp = c.get(url)
        flag = '' if resp.status_code < 500 else '  <-- SERVER ERROR'
        print(f"  {url:40s} {resp.status_code}{flag}")
        if resp.status_code >= 500:
            errors.append((username, url, resp.status_code))

print('')
if errors:
    print(f"COVERAGE CHECK FAILED: {len(errors)} server errors")
    for e in errors:
        print(' ', e)
else:
    print('COVERAGE CHECK PASSED: no server errors across all roles/pages')
