# from flask import redirect, abort, render_template, request
# from flask_restx import Resource, Namespace
# import stripe
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from ..models.users import User
# from ..utils import db
# from flask import current_app as app
# from decouple import config as configuration

# payment_namespace = Namespace("payment", "Namespace for paid scissor users")

# YOUR_DOMAIN = "http://localhost:5000/"

# products = {
#     "basic": {
#         "name": "Scissor - Basic",
#         "price_id": "price_1NOmNDBH2O8JhFAnC7yRjYb0",
#     },
#     "premium": {
#         "name": "Scissor - Premium",
#         "price_id": "price_1NPbXOBH2O8JhFAn6HRWolJW",
#     },
# }


# @payment_namespace.route("/subscription/<product_name>")
# class PaymentMethod(Resource):
#     @payment_namespace.doc(
#         description="Payment gateway for user using stripe. Any user can access",
#         params={"product_name": "Name of subscription plan"},
#     )
#     @jwt_required()
#     def post(self, product_name):
#         """
#         Payment gateway for user
#         """
#         user_id = get_jwt_identity()
#         user = User.get_by_id(user_id)

#         if product_name not in products:
#             abort(404)
#         checkout_session = stripe.checkout.Session.create(
#             line_items=[{"price": products[product_name]["price_id"], "quantity": 1}],
#             mode="subscription",
#             metadata={"user_id": str(user.id)},
#             success_url=YOUR_DOMAIN + "payment/success",  # YOUR DOMAIN + success.html
#             cancel_url=YOUR_DOMAIN + "payment/cancel",
#         )
#         app.logger.info(
#             f"User {user.username} initiated payment for {product_name} plan"
#         )

#         return redirect(checkout_session.url, code=303)


# @payment_namespace.route("/success")
# class PaymentSuccess(Resource):
#     def get(self):
#         """
#         Route for payment success
#         """
#         return render_template("success.html")


# @payment_namespace.route("/cancel")
# class PaymentFailure(Resource):
#     def get(self):
#         """
#         Route for failed payment
#         """
#         return render_template("cancel.html")


# @payment_namespace.route("/event")
# class PaidUserView(Resource):
#     @payment_namespace.doc(
#         description="Confirm payment success and give a user paid user privileges.",
#     )
#     def post(self):
#         """
#         Give a user paid privileges.
#         """
#         event = None
#         data = request.data
#         signature = request.headers["STRIPE_SIGNATURE"]

#         try:
#             event = stripe.Webhook.construct_event(
#                 data, signature, configuration("STRIPE_WEBHOOK_SECRET")
#             )
#         except ValueError as e:
#             return {"error": str(e)}, 400
#         except stripe.error.SignatureVerificationError as e:
#             return {"error": str(e)}, 400

#         if event["type"] == "checkout.session.completed":
#             session = stripe.checkout.Session.retrieve(
#                 event["data"]["object"].id, expand=["line_items"]
#             )
#             user_id = session.metadata.get("user_id")
#             user = User.query.get(user_id)
#             if user:
#                 user.paid = True
#                 db.session.commit()
#         app.logger.info(f"User {user.username} paid for a subsription plan")
#         return {"message": "Webhook received successfully."}
