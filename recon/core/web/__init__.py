from flask import Flask, request, abort, cli
from recon.core import base
from recon.core.constants import BANNER_WEB
from recon.core.web.db import Tasks
from redis import Redis
import os
import rq

# disable the development server warning banner
cli.show_server_banner = lambda *x: None

print(BANNER_WEB)

# create an application-wide framework and tasks instance
recon = base.Recon(check=False, analytics=False, marketplace=False)
recon.start(base.Mode.WEB)
tasks = Tasks(recon)

# configuration
DEBUG = False
SECRET_KEY = 'we keep no secrets here.'
JSON_SORT_KEYS = False
REDIS_URL = 'redis://'
WORKSPACE = recon.workspace.split('/')[-1]
print((f" * Workspace initialized: {WORKSPACE}"))

def create_app():

    # setting the static_url_path to blank serves static files from the web root
    app = Flask(__name__, static_url_path='')
    app.config.from_object(__name__)

    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('recon-tasks', connection=app.redis)

    @app.after_request
    def disable_cache(response):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response

    from recon.core.web.views import core
    app.register_blueprint(core)
    from recon.core.web.views import resources
    app.register_blueprint(resources)

    return app
