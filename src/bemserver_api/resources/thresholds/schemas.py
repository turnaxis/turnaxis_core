from datetime import datetime
import marshmallow as ma
import marshmallow_sqlalchemy as msa
from bemserver_api import AutoSchema
from bemserver_core.model.thresholds import Threshold

class ThresholdSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Threshold

    id = msa.auto_field(dump_only=True)
    value = msa.auto_field(required=True)
    device_id = msa.auto_field(required=True)
    user_id = msa.auto_field(required=True)
    created_at = msa.auto_field(dump_only=True, default=datetime.utcnow)
 