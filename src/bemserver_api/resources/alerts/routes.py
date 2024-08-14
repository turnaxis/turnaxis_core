from flask.views import MethodView
from flask_smorest import abort
from bemserver_core.model.alerts import Alert, Device, User
from bemserver_api import Blueprint
from bemserver_api.database import db
from .schemas import AlertSchema, AlertQueryArgsSchema
import marshmallow as ma


blp = Blueprint(
    "Alert", __name__, url_prefix="/alerts", description="Operations on alerts"
)

@blp.route("/")
class AlertViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(AlertQueryArgsSchema, location="query")
    @blp.response(200, AlertSchema(many=True))
    def get(self, args):
        """List alerts"""
        return Alert.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(AlertSchema)
    @blp.response(201, AlertSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new alert"""
        item = Alert.new(**new_item)
        db.session.commit()
        return item

@blp.route("/<int:item_id>")
class AlertByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, AlertSchema)
    def get(self, item_id):
        """Get alert by ID"""
        item = Alert.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(AlertSchema)
    @blp.response(200, AlertSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing alert"""
        item = Alert.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, AlertSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete an alert"""
        item = Alert.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, AlertSchema)
        item.delete()
        db.session.commit()

    @blp.route("/<int:item_id>/set_threshold", methods=("PUT",))
    @blp.login_required
    @blp.etag
    @blp.arguments(ma.Schema.from_dict({"threshold": ma.fields.Float(required=True)}))
    @blp.response(204)
    def set_threshold(args, item_id):
        """Set a custom threshold for a device"""
        item = Alert.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, AlertSchema)
        item.threshold = args["threshold"]
        db.session.commit()
        blp.set_etag(item, AlertSchema)

