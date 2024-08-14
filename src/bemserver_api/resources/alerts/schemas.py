import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_api import AutoSchema
from bemserver_core.model.alerts import Alert , AlertType, Device, User

class AlertSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Alert

    id = msa.auto_field(dump_only=True)
    alert_type = ma.fields.Enum(AlertType)
    threshold = msa.auto_field()
    actual_consumption = msa.auto_field()
    timestamp = msa.auto_field(dump_only=True)
    device_id = msa.auto_field()
    user_id = msa.auto_field()

class AlertQueryArgsSchema(ma.Schema):
    device_id = ma.fields.Int()
    user_id = ma.fields.Int()
    alert_type = ma.fields.Enum(AlertType)
    threshold = ma.fields.Float()
    actual_consumption = ma.fields.Float()
