from flask import request
from flask_restplus import Resource
from app.api.vat.serializers import vat_liability
from app.api.restplus import ns






@ns.route('/obligations')
class VatLiabilitiesCollection(Resource):

    def get(self):
        """
        Returns list of vat liabilities.
        """
        
         

        return {
      "start": "2017-01-01",
      "end": "2017-03-31",
      "due": "2017-05-07",
      "status": "F",
      "periodKey": "18A1",
      "received": "2017-05-06"
    }