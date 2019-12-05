import os
from app import celery, create_app

app = create_app(os.getenv('development') or 'development')
app.app_context().push()
