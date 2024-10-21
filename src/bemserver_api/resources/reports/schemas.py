import marshmallow as ma
from marshmallow import fields

class ReportSchema(ma.Schema):
    """Schema for representing report data."""
    id = fields.Int(description="Report ID")
    location = fields.Str(description="Location of the report")
    period_start = fields.Date(description="Start date of the report period")
    period_end = fields.Date(description="End date of the report period")
    consumption = fields.Float(description="Total power consumption")
    peak_usage_time = fields.Time(description="Peak usage time of the day")
    cost = fields.Float(description="Total cost of power usage")
    cost_savings = fields.Float(description="Cost savings")
    renewable_energy_utilization = fields.Float(description="Percentage of renewable energy used")
    co2_emissions = fields.Float(description="CO2 emissions")
    device_id = fields.Int(description="ID of the associated device")


    class Meta:
        ordered = True


class ReportQueryArgsSchema(ma.Schema):
    """Query arguments for generating reports."""

    location = fields.List(
        fields.Str(), 
        required=False, 
        description="Filter by location(s)"
    )

    period = fields.Str(
        validate=ma.validate.OneOf(
            ["last_12_months", "last_6_months", "last_31_days", "last_7_days", "custom"]
        ),
        required=True,
        description="Specify the time period for the report"
    )

    start_date = fields.Date(
        required=False, 
        description="Start date for custom date range"
    )
    end_date = fields.Date(
        required=False, 
        description="End date for custom date range"
    )

    report_type = fields.Str(
        validate=ma.validate.OneOf(
            [
                "consumption",
                "peak_usage_time",
                "cost",
                "cost_savings",
                "renewable_energy_utilization",
                "co2_emissions"
            ]
        ),
        required=True,
        description="The type of report to generate"
    )

    class Meta:
        ordered = True
