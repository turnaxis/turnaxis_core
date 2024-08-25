from flask.views import MethodView
from flask_smorest import abort
from bemserver_core.model.thresholds import Threshold
from bemserver_api import Blueprint
from bemserver_api.database import db
from .schemas import ThresholdSchema

blp = Blueprint("Threshold", __name__, url_prefix="/thresholds", description="Operations on thresholds")

@blp.route("/")
class ThresholdViews(MethodView):
    @blp.login_required
    @blp.arguments(ThresholdSchema)
    @blp.response(201, ThresholdSchema)
    def post(self, args):
        """Add a new threshold"""
        item = Threshold.new(**args)
        db.session.commit()
        return item

@blp.route("/<int:threshold_id>")
class ThresholdByIdViews(MethodView):
    @blp.login_required
    @blp.response(200, ThresholdSchema)
    def get(self, threshold_id):
        """Get threshold by ID"""
        item = Threshold.get_by_id(threshold_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.arguments(ThresholdSchema)
    @blp.response(200, ThresholdSchema)
    def put(self, args, threshold_id):
        """Update an existing threshold"""
        item = Threshold.get_by_id(threshold_id)
        if item is None:
            abort(404)
        item.update(**args)
        db.session.commit()
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, threshold_id):
        """Delete a threshold"""
        item = Threshold.get_by_id(threshold_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
 