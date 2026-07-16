import datetime
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from absence.models import AbsenceRecord
from dutyroster.models import DutyRoster
from personnel.models import Personnel
from strength.models import DailyStrength
from unitstructure.models import Appointment, Company, Platoon, Section

User = get_user_model()

RANKS_JCO_OR = [
    'Sub Maj', 'Sub', 'Nb Sub', 'Hav', 'Nk', 'L/Nk', 'Sep', 'Rfn',
]
FIRST_NAMES = [
    'Rajesh', 'Suresh', 'Vikram', 'Amit', 'Ravi', 'Anil', 'Sanjay', 'Deepak',
    'Manoj', 'Ashok', 'Vijay', 'Sunil', 'Rakesh', 'Naveen', 'Pradeep', 'Ajay',
    'Vinod', 'Ramesh', 'Mahesh', 'Dinesh', 'Gurpreet', 'Harpal', 'Balwinder',
    'Jaswant', 'Karan', 'Mohan', 'Naresh', 'Om', 'Pawan', 'Ranjit', 'Satish',
    'Tarun', 'Umesh', 'Yogesh', 'Baldev', 'Chander', 'Devendra', 'Ishwar',
]
LAST_NAMES = [
    'Kumar', 'Singh', 'Sharma', 'Verma', 'Yadav', 'Rana', 'Chauhan', 'Rawat',
    'Thapa', 'Gurung', 'Negi', 'Bisht', 'Mehta', 'Chand', 'Gill', 'Malik',
    'Rathore', 'Shekhawat', 'Pandey', 'Tiwari', 'Reddy', 'Nair', 'Pillai',
]
APPOINTMENTS = [
    ('Rifleman', 'General duty infantry soldier'),
    ('Section Commander', 'Commands a section'),
    ('Platoon Havildar', 'Senior NCO of a platoon'),
    ('Company Clerk', 'Administrative clerk of the company'),
    ('Driver', 'Unit transport driver'),
    ('Signaller', 'Communications duties'),
    ('Cook', 'Unit kitchen staff'),
    ('Nursing Assistant', 'Regimental Medical Aid Post staff'),
    ('Storeman', 'Company Quartermaster store staff'),
    ('Sniper', 'Trained designated marksman (administrative record only)'),
]
COMPANIES = [
    ('HQ Coy', 'HQ'),
    ('A Coy', 'A'),
    ('B Coy', 'B'),
    ('C Coy', 'C'),
    ('D Coy', 'D'),
    ('Support Coy', 'SP'),
]
DUTY_TYPES = ['Quarter Guard', 'Orderly Officer', 'Orderly NCO', 'Fire Picket', 'Fatigue', 'Kitchen Duty', 'Ceremonial Guard']
DUTY_LOCATIONS = ['Unit Lines', 'Quarter Guard', 'Officers Mess', 'Unit Main Gate', 'Admin Block', 'MI Room']


class Command(BaseCommand):
    help = 'Seed the database with demo/sample data for the Unit Administration System (safe to re-run).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush-personnel', action='store_true',
            help='Delete existing demo personnel/absence/strength/duty records before reseeding.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)
        today = timezone.localdate()

        self.stdout.write('Seeding unit structure...')
        companies = self._seed_companies()
        platoons_by_company = self._seed_platoons(companies)
        sections_by_platoon = self._seed_sections(platoons_by_company)
        appointments = self._seed_appointments()

        self.stdout.write('Seeding demo user accounts...')
        self._seed_users(companies)

        if options['flush_personnel']:
            self.stdout.write('Flushing existing demo personnel/absence/strength/duty records...')
            DutyRoster.objects.all().delete()
            AbsenceRecord.objects.all().delete()
            DailyStrength.objects.all().delete()
            Personnel.objects.all().delete()

        self.stdout.write('Seeding personnel...')
        personnel_list = self._seed_personnel(companies, platoons_by_company, sections_by_platoon, appointments, today)

        self.stdout.write('Seeding absence/leave/TD records...')
        self._seed_absence(personnel_list, today)

        self.stdout.write('Seeding daily strength returns...')
        self._seed_strength(companies, personnel_list, today)

        self.stdout.write('Seeding duty roster entries...')
        self._seed_duty(companies, personnel_list, today)

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Demo login accounts (CHANGE PASSWORDS before real use):'))
        self.stdout.write('  superadmin   / Sup3rAdmin!2024   (Super Admin)')
        self.stdout.write('  adjt_admin   / AdjtAdmin!2024    (Adjt / Admin Branch)')
        self.stdout.write('  clerk_acoy   / ClerkACoy!2024    (Company Clerk - A Coy)')
        self.stdout.write('  clerk_bcoy   / ClerkBCoy!2024    (Company Clerk - B Coy)')
        self.stdout.write('  viewer1      / Viewer1!2024      (Viewer)')

    def _seed_companies(self):
        companies = {}
        for name, code in COMPANIES:
            company, _ = Company.objects.get_or_create(code=code, defaults={'name': name})
            companies[code] = company
        return companies

    def _seed_platoons(self, companies):
        platoons_by_company = {}
        for code, company in companies.items():
            platoon_names = ['HQ Element'] if code == 'HQ' else ['1 Platoon', '2 Platoon', '3 Platoon']
            platoons = []
            for name in platoon_names:
                platoon, _ = Platoon.objects.get_or_create(company=company, name=name)
                platoons.append(platoon)
            platoons_by_company[code] = platoons
        return platoons_by_company

    def _seed_sections(self, platoons_by_company):
        sections_by_platoon = {}
        for platoons in platoons_by_company.values():
            for platoon in platoons:
                sections = []
                for i in range(1, 4):
                    section, _ = Section.objects.get_or_create(platoon=platoon, name=f'Section {i}')
                    sections.append(section)
                sections_by_platoon[platoon.id] = sections
        return sections_by_platoon

    def _seed_appointments(self):
        appointments = []
        for name, description in APPOINTMENTS:
            appointment, _ = Appointment.objects.get_or_create(name=name, defaults={'description': description})
            appointments.append(appointment)
        return appointments

    def _seed_users(self, companies):
        def ensure_user(username, password, role, company=None, first_name='', last_name='', is_staff=False, is_superuser=False):
            user, created = User.objects.get_or_create(username=username, defaults={
                'role': role,
                'company': company,
                'first_name': first_name,
                'last_name': last_name,
                'is_staff': is_staff,
                'is_superuser': is_superuser,
            })
            if created:
                user.set_password(password)
                user.save()
            return user

        ensure_user('superadmin', 'Sup3rAdmin!2024', 'SUPER_ADMIN', first_name='Unit', last_name='Super Admin', is_staff=True, is_superuser=True)
        ensure_user('adjt_admin', 'AdjtAdmin!2024', 'ADMIN_ADJT', first_name='Adjt', last_name='Admin Branch', is_staff=True)
        ensure_user('clerk_acoy', 'ClerkACoy!2024', 'CLERK', company=companies['A'], first_name='Clerk', last_name='A Coy')
        ensure_user('clerk_bcoy', 'ClerkBCoy!2024', 'CLERK', company=companies['B'], first_name='Clerk', last_name='B Coy')
        ensure_user('viewer1', 'Viewer1!2024', 'VIEWER', first_name='Unit', last_name='Viewer')

    def _seed_personnel(self, companies, platoons_by_company, sections_by_platoon, appointments, today):
        personnel_list = list(Personnel.objects.all())
        if personnel_list:
            return personnel_list

        statuses = [
            Personnel.STATUS_PRESENT, Personnel.STATUS_PRESENT, Personnel.STATUS_PRESENT,
            Personnel.STATUS_PRESENT, Personnel.STATUS_PRESENT, Personnel.STATUS_LEAVE,
            Personnel.STATUS_TD, Personnel.STATUS_COURSE, Personnel.STATUS_HOSPITAL,
            Personnel.STATUS_ATTACHED_OUT,
        ]

        used_names = set()
        army_no_counter = 1000
        for code, company in companies.items():
            platoons = platoons_by_company[code]
            count = 8 if code == 'HQ' else 25
            for i in range(count):
                platoon = platoons[i % len(platoons)]
                sections = sections_by_platoon.get(platoon.id, [])
                section = sections[i % len(sections)] if sections else None
                appointment = random.choice(appointments)
                rank = random.choice(RANKS_JCO_OR)

                while True:
                    first = random.choice(FIRST_NAMES)
                    last = random.choice(LAST_NAMES)
                    key = f"{first} {last} {army_no_counter}"
                    if key not in used_names:
                        used_names.add(key)
                        break

                army_no_counter += 1
                army_number = f"{army_no_counter}{code}"
                status = random.choice(statuses)
                joining_days_ago = random.randint(60, 3000)

                person = Personnel.objects.create(
                    army_number=army_number,
                    rank=rank,
                    full_name=f"{first} {last}",
                    company=company,
                    platoon=platoon,
                    section=section,
                    appointment=appointment,
                    date_of_joining_unit=today - datetime.timedelta(days=joining_days_ago),
                    status=status,
                    is_active=True,
                )
                personnel_list.append(person)
        return personnel_list

    def _seed_absence(self, personnel_list, today):
        if AbsenceRecord.objects.exists():
            return

        type_map = {
            Personnel.STATUS_LEAVE: AbsenceRecord.TYPE_LEAVE,
            Personnel.STATUS_TD: AbsenceRecord.TYPE_TD,
            Personnel.STATUS_COURSE: AbsenceRecord.TYPE_COURSE,
            Personnel.STATUS_HOSPITAL: AbsenceRecord.TYPE_HOSPITAL,
            Personnel.STATUS_ATTACHED_OUT: AbsenceRecord.TYPE_ATTACHMENT,
        }
        destinations = ['Home Town', 'Command Hospital', 'Leave Station', 'Training Establishment', 'Family Accommodation']

        for person in personnel_list:
            absence_type = type_map.get(person.status)
            if not absence_type:
                continue
            from_date = today - datetime.timedelta(days=random.randint(0, 5))
            to_date = from_date + datetime.timedelta(days=random.randint(3, 20))
            AbsenceRecord.objects.create(
                person=person,
                type=absence_type,
                from_date=from_date,
                to_date=to_date,
                authority_reference=f"Adm/{person.company.code}/{random.randint(100, 999)}/2024",
                destination=random.choice(destinations),
                status=AbsenceRecord.STATUS_ONGOING if from_date <= today <= to_date else AbsenceRecord.STATUS_PLANNED,
            )

        # A handful of already-returned/cancelled historical records for report variety.
        sample = random.sample(personnel_list, min(10, len(personnel_list)))
        for person in sample:
            from_date = today - datetime.timedelta(days=random.randint(30, 90))
            to_date = from_date + datetime.timedelta(days=random.randint(3, 15))
            AbsenceRecord.objects.create(
                person=person,
                type=random.choice([AbsenceRecord.TYPE_LEAVE, AbsenceRecord.TYPE_TD, AbsenceRecord.TYPE_COURSE]),
                from_date=from_date,
                to_date=to_date,
                authority_reference=f"Adm/{person.company.code}/{random.randint(100, 999)}/2024",
                destination=random.choice(destinations),
                status=AbsenceRecord.STATUS_RETURNED,
            )

    def _seed_strength(self, companies, personnel_list, today):
        if DailyStrength.objects.exists():
            return

        for day_offset in range(6, -1, -1):
            date = today - datetime.timedelta(days=day_offset)
            for code, company in companies.items():
                company_personnel = [p for p in personnel_list if p.company_id == company.id]
                total = len(company_personnel)
                present = sum(1 for p in company_personnel if p.status == Personnel.STATUS_PRESENT)
                leave = sum(1 for p in company_personnel if p.status == Personnel.STATUS_LEAVE)
                td = sum(1 for p in company_personnel if p.status == Personnel.STATUS_TD)
                course = sum(1 for p in company_personnel if p.status == Personnel.STATUS_COURSE)
                hospital = sum(1 for p in company_personnel if p.status == Personnel.STATUS_HOSPITAL)
                attached_out = sum(1 for p in company_personnel if p.status == Personnel.STATUS_ATTACHED_OUT)
                other = total - (present + leave + td + course + hospital + attached_out)
                DailyStrength.objects.create(
                    date=date,
                    company=company,
                    total_posted_strength=total,
                    present=present,
                    leave=leave,
                    temporary_duty=td,
                    course=course,
                    hospital_sick=hospital,
                    attached_out=attached_out,
                    other_absence=max(other, 0),
                )

    def _seed_duty(self, companies, personnel_list, today):
        if DutyRoster.objects.exists():
            return

        for day_offset in range(-3, 5):
            date = today + datetime.timedelta(days=day_offset)
            for code, company in list(companies.items())[:4]:
                company_personnel = [p for p in personnel_list if p.company_id == company.id and p.status == Personnel.STATUS_PRESENT]
                if not company_personnel:
                    continue
                detailed = random.sample(company_personnel, min(2, len(company_personnel)))
                status = DutyRoster.STATUS_COMPLETED if day_offset < 0 else (
                    DutyRoster.STATUS_SCHEDULED if day_offset >= 0 else DutyRoster.STATUS_SCHEDULED
                )
                duty = DutyRoster.objects.create(
                    duty_date=date,
                    duty_type=random.choice(DUTY_TYPES),
                    company=company,
                    duty_location=random.choice(DUTY_LOCATIONS),
                    shift_time='0600-1400 hrs' if day_offset % 2 == 0 else '1400-2200 hrs',
                    status=status,
                )
                duty.personnel_detailed.set(detailed)
