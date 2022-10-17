"""Energy consumption timeseries by buildings API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EnergyConsumptionTimeseriesByBuilding

from bemserver_api import AutoSchema, Schema


class EnergyConsumptionTimeseriesByBuildingSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = EnergyConsumptionTimeseriesByBuilding.__table__

    id = msa.auto_field(dump_only=True)


class EnergyConsumptionTimeseriesByBuildingQueryArgsSchema(Schema):
    campaign_id = ma.fields.Int()
    building_id = ma.fields.Int()
    source_id = ma.fields.Int()
    end_use_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
