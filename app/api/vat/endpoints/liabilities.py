from flask import request
from flask_restplus import Resource
from app.api.vat.serializers import vat_liability
from app.api.restplus import ns







@ns.route('/liabilities')
class VatLiabilitiesCollection(Resource):

    def get(self):
        """
        Returns list of vat liabilities.
        """
        
         

        return {'hey': 'there'}
