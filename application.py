from flask import Flask
from flask_cors import CORS
from .containers import Container
from . import main


def create_app() -> Flask:
    container = Container()
    app = Flask(__name__)
    CORS(app, support_credentials=True)
    app.container = container
    app.add_url_rule("/", "index", main.index)
    app.add_url_rule("/get-data-from-gpt","getDataFromGPT",main.run, methods = ['POST'])
    # app.add_url_rule("/get-data-from-gpt", "getDataFromGPT", views.getDataFromGPT,  methods=['GET'])
    # app.add_url_rule("/get-location","getLocations",locations.getLocations, methods =['GET'])
    # app.add_url_rule("/media-upload","upload_images",upload.upload_images, methods = ['POST'])

    return app


