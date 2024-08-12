import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_api import Schema, AutoSchema
from bemserver_core.model import Device, DeviceCategory, DeviceByTimeseries
from bemserver_core.model.device import DeviceStatus


class DeviceGetQueryArgsSchema(Schema):
    name = ma.fields.Str()
    building_id = ma.fields.Int()
    unique_identifier = ma.fields.Str()
    status = ma.fields.Enum(DeviceStatus)
    energy_rating = ma.fields.Str()
    installation = ma.fields.Date()
    manufacturer = ma.fields.Str()
    model = ma.fields.Str()
    device_category_id = ma.fields.Int()


class DeviceSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Device

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 50))
    status = ma.fields.Enum(DeviceStatus)


class DeviceCategorySchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = DeviceCategory

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 50))


class DeviceResponseSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Device
    
    id = msa.auto_field(dump_only=True)
    status = ma.fields.Enum(DeviceStatus)
    device_category = ma.fields.Nested(DeviceCategorySchema(), dump_only=True)


class DeviceByTimeSeriesSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = DeviceByTimeseries