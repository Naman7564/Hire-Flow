#!/bin/bash

echo "===========================================" 
echo "  HireFlow — Waiting for MySQL..."
echo "===========================================" 

# Wait for MySQL to be ready
while ! nc -z $MYSQL_HOST $MYSQL_PORT; do
    echo "MySQL is unavailable — sleeping..."
    sleep 2
done

echo "MySQL is up — starting migrations..."

# Run migrations
python manage.py makemigrations accounts jobs applications dashboard --noinput
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Create superuser if not exists
python manage.py shell -c "
from accounts.models import User
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser('admin', 'admin@hireflow.com', 'admin123')
    user.role = 'hr'
    user.first_name = 'Admin'
    user.last_name = 'HR'
    user.save()
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
"

echo "===========================================" 
echo "  HireFlow — Starting Gunicorn server..."
echo "===========================================" 

# Start Gunicorn
exec gunicorn hr_hiring.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
