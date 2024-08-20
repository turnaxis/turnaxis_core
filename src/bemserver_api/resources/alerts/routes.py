from flask.views import MethodView
from flask_smorest import abort
from bemserver_core.model.alerts import Alert, Threshold
from bemserver_api import Blueprint
from bemserver_api.database import db
from .schemas import AlertSchema, AlertQueryArgsSchema, ThresholdSchema
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
class SetThreshold(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(ThresholdSchema)
    @blp.response(204)
    def put(self, args, item_id):
        """Set a custom threshold for a device"""
        threshold = Threshold.get_by_device_user(args["device_id"], args["user_id"])
        if threshold is None:
            threshold = Threshold.new(**args)
        else:
            threshold.update(**args)
        db.session.commit()
        return "", 204

