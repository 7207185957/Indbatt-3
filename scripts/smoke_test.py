"""
Quick functional smoke test exercising the major flows described in the
task: login, RBAC scoping, CRUD, CSV export. Not a substitute for a full
pytest/unittest suite, but useful for a fast end-to-end sanity check
during development. Safe to delete before shipping if not desired.

Run with:  python manage.py shell -c "exec(open('scripts/smoke_test.py').read())"
"""
import datetime

import django
from django.test import Client
from django.test.utils import setup_test_environment
from django.urls import reverse

from absence.models import AbsenceRecord
from personnel.models import Personnel
from unitstructure.models import Company

setup_test_environment()

FAILURES = []


def check(label, condition):
    status = 'OK' if condition else 'FAIL'
    print(f"[{status}] {label}")
    if not condition:
        FAILURES.append(label)


# ---- Login as superadmin ----
c = Client()
resp = c.post('/login/', {'username': 'superadmin', 'password': 'Sup3rAdmin!2024'})
check('superadmin login redirects', resp.status_code == 302)

resp = c.get('/dashboard/')
check('dashboard loads for superadmin', resp.status_code == 200)
check('dashboard shows total_active', 'total_active' in resp.context)

# ---- Personnel CRUD ----
hq = Company.objects.get(code='HQ')
resp = c.post('/personnel/add/', {
    'army_number': 'SMOKE001',
    'rank': 'Sep',
    'full_name': 'Smoke Test Soldier',
    'company': hq.pk,
    'date_of_joining_unit': '2023-01-15',
    'status': 'PRESENT',
    'is_active': 'on',
})
check('personnel create redirects (302)', resp.status_code == 302)
person = Personnel.objects.filter(army_number='SMOKE001').first()
check('personnel record created', person is not None)
if person:
    check('created_by stamped', person.created_by is not None and person.created_by.username == 'superadmin')

    resp = c.get(f'/personnel/{person.pk}/')
    check('personnel detail view loads', resp.status_code == 200)

    resp = c.post(f'/personnel/{person.pk}/edit/', {
        'army_number': 'SMOKE001',
        'rank': 'Nk',
        'full_name': 'Smoke Test Soldier',
        'company': hq.pk,
        'date_of_joining_unit': '2023-01-15',
        'status': 'PRESENT',
        'is_active': 'on',
    })
    check('personnel edit redirects (302)', resp.status_code == 302)
    person.refresh_from_db()
    check('personnel edit persisted', person.rank == 'Nk')
    check('updated_by stamped', person.updated_by is not None and person.updated_by.username == 'superadmin')

# ---- Absence create ----
resp = c.post('/absence/add/', {
    'person': person.pk,
    'type': 'LEAVE',
    'from_date': '2026-07-10',
    'to_date': '2026-07-20',
    'authority_reference': 'Adm/Test/001',
    'destination': 'Home Town',
    'status': 'ONGOING',
})
check('absence create redirects (302)', resp.status_code == 302)
absence = AbsenceRecord.objects.filter(person=person).first()
check('absence record created', absence is not None)

# ---- Daily strength: duplicate prevention ----
resp = c.post('/strength/add/', {
    'date': '2026-08-01',
    'company': hq.pk,
    'total_posted_strength': 10,
    'present': 8,
    'leave': 1,
    'temporary_duty': 0,
    'course': 0,
    'hospital_sick': 0,
    'attached_out': 0,
    'other_absence': 1,
    'remarks': 'smoke test entry',
})
check('strength first entry redirects (302)', resp.status_code == 302)
resp = c.post('/strength/add/', {
    'date': '2026-08-01',
    'company': hq.pk,
    'total_posted_strength': 10,
    'present': 8,
    'leave': 1,
    'temporary_duty': 0,
    'course': 0,
    'hospital_sick': 0,
    'attached_out': 0,
    'other_absence': 1,
    'remarks': 'duplicate attempt',
})
check('duplicate strength entry rejected (200, not redirect)', resp.status_code == 200)
check('duplicate strength entry shows form error', b'already exists' in resp.content)

# ---- Reports CSV export ----
resp = c.get('/reports/personnel/export/')
check('personnel report CSV export works', resp.status_code == 200 and resp['Content-Type'] == 'text/csv')

# ---- RBAC: Company Clerk scoping ----
c2 = Client()
resp = c2.post('/login/', {'username': 'clerk_acoy', 'password': 'ClerkACoy!2024'})
check('clerk login redirects', resp.status_code == 302)

resp = c2.get('/personnel/')
own_company_only = all(p.company.code == 'A' for p in resp.context['personnel_list'])
check('clerk sees only own company personnel', own_company_only)

resp = c2.get(f'/personnel/{person.pk}/')
check(
    'clerk denied access to other-company personnel detail (404, scoped queryset hides it)',
    resp.status_code == 404,
)

b_coy = Company.objects.get(code='B')
resp = c2.post('/personnel/add/', {
    'army_number': 'SMOKE002',
    'rank': 'Sep',
    'full_name': 'Cross Company Attempt',
    'company': b_coy.pk,
    'date_of_joining_unit': '2023-01-15',
    'status': 'PRESENT',
    'is_active': 'on',
})
check(
    'clerk cannot create personnel for another company (form rejects invalid company choice)',
    resp.status_code == 200 and not Personnel.objects.filter(army_number='SMOKE002').exists(),
)

# ---- RBAC: Viewer cannot access add pages ----
c3 = Client()
resp = c3.post('/login/', {'username': 'viewer1', 'password': 'Viewer1!2024'})
check('viewer login redirects', resp.status_code == 302)
resp = c3.get('/personnel/add/')
check('viewer denied personnel add (403)', resp.status_code == 403)
resp = c3.get('/personnel/')
check('viewer can view personnel list (200)', resp.status_code == 200)

# ---- RBAC: non-super-admin cannot manage users ----
c4 = Client()
c4.post('/login/', {'username': 'adjt_admin', 'password': 'AdjtAdmin!2024'})
resp = c4.get('/accounts/users/')
check('adjt_admin denied user management (403)', resp.status_code == 403)

# ---- Unauthenticated access redirects to login ----
c5 = Client()
resp = c5.get('/dashboard/')
check('anonymous user redirected to login', resp.status_code == 302 and '/login/' in resp['Location'])

print('')
if FAILURES:
    print(f"SMOKE TEST FAILED ({len(FAILURES)} failures):")
    for f in FAILURES:
        print(f"  - {f}")
else:
    print('ALL SMOKE TESTS PASSED')
