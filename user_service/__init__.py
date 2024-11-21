from flask import Flask
from shared.config import Config
from flasgger import Swagger

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
swagger = Swagger(app)

from . import routes
