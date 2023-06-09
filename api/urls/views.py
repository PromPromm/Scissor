from flask_restx import Namespace, Resource, fields
from flask import abort, request, redirect, send_file
from ..models.users import User
from ..models.urls import Url
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus
from ..utils import db, generate_url_key
import validators
import qrcode
import io

url_namespace = Namespace("url", "Namespace for urls")

url_model = url_namespace.model(
    "url",
    {
        "name": fields.String(description="Name of shortened url"),
        "target url": fields.String(description="Target URL"),
        "key": fields.String(description="The new string for url"),
    },
)


@url_namespace.route("/")
class CreateURLView(Resource):
    @url_namespace.expect(url_model)
    @url_namespace.doc(
        description="Shorten a url. Paid users can customize their url and users on the free plan get a random string assigned"
    )
    @jwt_required()
    def post(self):
        """
        Shorten a url
        """
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)

        data = request.get_json()

        if not validators.url(data.get("target url")):
            abort(400, "Your provided URL is not valid")

        if user.paid:
            url = Url(
                name=data.get("name"),
                key=data.get("key"),
                target_url=data.get("target url"),
            )
        else:
            url = Url(
                name=data.get("name"),
                key=generate_url_key(5),
                target_url=data.get("target url"),
            )
        url.user_id = user_id
        url.save()
        return {"message": "URL CREATED"}, HTTPStatus.OK


@url_namespace.route("/<string:url_key>")
class RedirectURLView(Resource):
    @url_namespace.doc(
        description="Redirect a URL", params={"url_key": "The shortened url key"}
    )
    def get(self, url_key):
        """
        Redirect shorten url to target url
        """
        url = Url.get_by_key(url_key)
        if url:
            url.clicks += 1
            db.session.commit()
            return redirect(url.target_url)
        return {"message": "NOT FOUND"}, HTTPStatus.NOT_FOUND

    @url_namespace.doc(
        description="Delete a shortened URL.",
        params={"url_key": "The shortened url key"},
    )
    @jwt_required()
    def delete(self, url_key):
        """
        Delete a url
        """
        url = Url.get_by_key(url_key)
        if url:
            url.is_active = False
            db.session.commit()
            return {"message": "Url has been deleted"}, HTTPStatus.OK
        return {"message": "NOT FOUND"}, HTTPStatus.NOT_FOUND


@url_namespace.route("/<string:url_key>/qrcode")
class QRCodeGenerationView(Resource):
    def post(self, url_key):
        url = Url.get_by_key(url_key)
        if url:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(url.target_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="blue", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer)
            buffer.seek(0)
            response = send_file(buffer, mimetype="image/png")
            return response
        return {"message": "NOT FOUND"}, HTTPStatus.NOT_FOUND
