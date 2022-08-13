#!/usr/bin/env bash
python manage.py migrate
echo "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('admin', 'pass')" | python manage.py shell
python manage.py runserver 0.0.0.0:8000