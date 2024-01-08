import subprocess
import os
import time

# Define the Celery worker and beat commands
server_command = "python manage.py runserver"
worker_command = "celery -A celery_app worker --loglevel=info -P eventlet"
beat_command = "celery -A celery_app beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=info"
redis_command = "redis-server --port 6380 --slaveof 127.0.0.1 6379"


# Function to run a command in the background
def run_command_in_background(command):
    subprocess.Popen(command, shell=True)

if __name__ == "__main__":
    # Start Celery worker and beat in the background
    subprocess.run(server_command, shell=True)

    run_command_in_background(worker_command)
    run_command_in_background(beat_command)

    run_command_in_background(redis_command)

    # Start Django development server


