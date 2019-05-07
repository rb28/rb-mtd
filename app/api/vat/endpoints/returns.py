from flask import request
from flask_restplus import Resource
from app.api.vat.serializers import vat_return
from app.api.restplus import ns



@ns.route('/returns')
class Returns(Resource):
    def get(self):
        """
        Returns list of vat returns.
        """
        return {'task': 'Hello world'}, 201



