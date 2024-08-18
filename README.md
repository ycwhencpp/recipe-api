https://recipe-api-bf6x.onrender.com/
# Live Server Consideration

- **500 Error During Recipe Liking**: If a 500 error occurs when liking a recipe, it might be due to Celery workers being inactive in a free-trail plan.
# Setup Instructions

## Using Docker 
```bash
sudo docker-compose build # Run from the root dir.
sudo docker-compose up
```

## Installation 
```bash
pip3 install -r requirements.txt  # Run from the root dir.
python3 manage.py makemigrations
python3.manage.py migrate
python3 manage.py runserver
```

## Points to Consider

- **PostgreSQL**: Ensure PostgreSQL is running with `sudo service postgresql start`.
- **Redis**: Ensure Redis is running with `sudo service redis start`.

## Database Setup

```bash
sudo -i -u postgres
psql
CREATE DATABASE db_name;
CREATE USER db_user WITH ENCRYPTED PASSWORD 'db_password';
GRANT ALL PRIVILEGES ON DATABASE db_name TO db_user;
\q
```

## Setting Up the .env File

```bash
SECRET_KEY='your_secret_key'
DB_NAME='db_name'
DB_USERNAME='db_user'
DB_PASSWORD='db_password'
DB_HOSTNAME='localhost'
DB_PORT=5432  # or your preferred port
ENVIRONMENT='development'
```

## Starting Celery Workers

```bash
redis-server
python manage.py migrate django_celery_beat
celery -A config.settings.celery worker --loglevel=info
celery -A config.settings.celery beat --loglevel=debug
```

# Running Tests

```bash
python3 manage.py test
```

## Generating Coverage Reports

```bash
coverage run --source='.' manage.py test
coverage report -m
coverage html 
open htmlcov/index.html
```

# Scalability

- **Recipe Like Notifications**: To extend the functionality to send weekly, bi-weekly, or monthly notifications, add the necessary columns to the `recipe_like_notifications` table.

- **Mail Queue**: The `mail_queue` is a temporary queue for storing various types of emails. Set up a cron job to truncate the `mail_queue` weekly or monthly, depending on our needs.

- **Mail Stats**: The `mail_stats` table is a permanent record of all emails sent through the platform.

- **Cron Job**: A cron job runs every 10 minutes to process potential emails in the `mail_queue`. You can schedule emails by adding rows to this table, another cron runs at 12:00 Am to process potential notifications from `recipe_like_notifications`.

- **Time-Specific Emails**: To send emails at specific times, we can add a `to_send_after` column to the `mail_queue` to define the desired timeframe.
