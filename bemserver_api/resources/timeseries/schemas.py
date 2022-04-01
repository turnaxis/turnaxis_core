"""Timeseries API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Timeseries

from bemserver_api import AutoSchema, Schema


class TimeseriesSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = Timeseries.__table__
        exclude = ("_campaign_id", "_campaign_scope_id")

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    campaign_id = ma.fields.Int(required=True)
    campaign_scope_id = ma.fields.Int(required=True)
    unit_symbol = msa.auto_field(validate=ma.validate.Length(1, 20))


class TimeseriesPutSchema(TimeseriesSchema):
    class Meta(TimeseriesSchema.Meta):
        exclude = TimeseriesSchema.Meta.exclude + ("campaign_id", "campaign_scope_id")


class TimeseriesQueryArgsSchema(Schema):
    name = ma.fields.Str()
    unit_symbol = ma.fields.Str()
    campaign_id = ma.fields.Int()
    user_id = ma.fields.Int()
