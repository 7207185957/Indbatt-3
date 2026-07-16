from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('unitstructure', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardAnnouncement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=300)),
                ('priority', models.CharField(choices=[('INFO', 'Information'), ('IMPORTANT', 'Important'), ('URGENT', 'Urgent')], default='INFO', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('starts_on', models.DateField(blank=True, null=True)),
                ('ends_on', models.DateField(blank=True, null=True)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={'ordering': ['order', '-id']},
        ),
        migrations.CreateModel(
            name='DashboardHeroSlide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('subtitle', models.CharField(blank=True, max_length=250)),
                ('image', models.ImageField(blank=True, null=True, upload_to='dashboard_slides/')),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={'ordering': ['order', 'id']},
        ),
        migrations.CreateModel(
            name='UnitEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('event_type', models.CharField(choices=[('EVENT', 'Event'), ('BIRTHDAY', 'Birthday'), ('REMINDER', 'Reminder')], default='EVENT', max_length=20)),
                ('event_date', models.DateField()),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dashboard_events', to='unitstructure.company')),
            ],
            options={'ordering': ['event_date', 'title']},
        ),
    ]
