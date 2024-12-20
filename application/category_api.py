from flask_restful import Resource
from application.extensions import api, db
from application.models import Service
from application.auth import role_required
from flask_jwt_extended import jwt_required

class CategoriesAPI(Resource):
    @jwt_required()
    def get(self):
        categories = db.session.query(Service.category, Service.category_image).distinct().all()
        if not categories:
            return {"message": "No categories available"}, 404
        categories_data = [
            {"name": category[0], "image_url": category[1]} for category in categories
        ]
        return categories_data, 201
        
api.add_resource(CategoriesAPI, '/categories')

