from flask.views import MethodView

from flask_smorest import abort

from bemserver_core.model import Device
from bemserver_core.model.device import DeviceStatus
from bemserver_api import Blueprint
from bemserver_api.database import db

from .schema import DeviceSchema, DeviceGetQueryArgsSchema

blp = Blueprint(
    "Device",
    __name__,
    url_prefix="/api/v1/devices",
    description="Operations on devices",
)


@blp.route("/")
class DevicesViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, DeviceSchema(many=True))
    def get(self):
        """List devices"""
        return Device.get()

    @blp.login_required
    @blp.etag
    @blp.arguments(DeviceSchema)
    @blp.response(201, DeviceSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add new device"""
        item = Device.new(**new_item)
        db.session.commit()
        return item
