from flask import Flask
from shared.config import Config
from flasgger import Swagger

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Authentication Service API',
    'uiversion': 3
}
swagger = Swagger(app)

from . import routes
