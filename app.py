from application import app
from application.celery.celery_factory import celery_init_app

celery_app = celery_init_app(app)

import application.celery.celery_schedule

if __name__ == '__main__':
    app.run(host='localhost', port=5000)