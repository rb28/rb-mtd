from flask_restplus import fields
from app.api.restplus import api

vat_return = api.model('VAT return', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a blog post'),
    
})

vat_obligation = api.model('VAT obligation', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a blog post'),
    
})

vat_liability = api.model('VAT liability', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a blog post'),
    
})

organisation = api.model('Organisation', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of an Organisation'),
    'code': fields.String(required=True, description='Organisation code'),
    'name': fields.String(required=True, description='Organisation short name'),
    'vrn': fields.String(required=True, description='Organisation Vat registration number')
})



