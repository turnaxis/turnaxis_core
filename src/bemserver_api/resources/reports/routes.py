from flask.views import MethodView
from flask_smorest import abort
from flask import request, jsonify, send_file
from datetime import datetime, timedelta
from io import StringIO
import csv

from bemserver_api import Blueprint
from bemserver_api.database import db
from bemserver_core.model.reports import Report
from .schemas import ReportSchema, ReportQueryArgsSchema
from bemserver_core.model.reports import get_report_by_location, get_general_report

blp = Blueprint(
    "Reports", __name__, url_prefix="/api/v1/reports", description="Operations on reports"
)

@blp.route("/")
class ReportViews(MethodView):
    @blp.arguments(ReportQueryArgsSchema, location="query")
    @blp.response(200, ReportSchema(many=True))
    def get(self, args):
        """Get report by location and custom period"""
        location = args.get('location')
        period_start = args.get('period_start')
        period_end = args.get('period_end')

        if not location or not period_start or not period_end:
            abort(400, message="location, period_start, and period_end are required")

        try:
            period_start = datetime.fromisoformat(period_start)
            period_end = datetime.fromisoformat(period_end)
        except ValueError:
            abort(400, message="Invalid date format")

        reports = get_report_by_location(db.session, location, period_start, period_end)
        return reports
    
    @blp.arguments(ReportSchema)
    @blp.response(201, ReportSchema)
    def post(self, new_data):
        """Create a new report"""
        # Extract the data and create a new report instance
        report = Report(
            location=new_data['location'],
            period_start=new_data['period_start'],
            period_end=new_data['period_end'],
            consumption=new_data['consumption'],
            cost=new_data['cost'],
            co2_emissions=new_data['co2_emissions'],
            renewable_energy_utilization=new_data['renewable_energy_utilization'],
            peak_usage_time=new_data['peak_usage_time'],
            cost_savings=new_data.get('cost_savings'),  # Optional field
            device_id=new_data['device_id']
        )

        # Add the report to the session and commit
        db.session.add(report)
        db.session.commit()

        return report, 201

@blp.route("/general")
class GeneralReportViews(MethodView):
    @blp.arguments(ReportQueryArgsSchema, location="query")
    @blp.response(200, ReportSchema(many=True))
    def get(self, args):
        """Get general report based on predefined period"""
        period = args.get('period')

        # Define period ranges
        today = datetime.utcnow()
        if period == 'last_7_days':
            period_start = today - timedelta(days=7)
        elif period == 'last_31_days':
            period_start = today - timedelta(days=31)
        elif period == 'last_6_months':
            period_start = today - timedelta(days=6*30)
        elif period == 'last_12_months':
            period_start = today - timedelta(days=12*30)
        else:
            abort(400, message="Invalid period value")

        reports = get_general_report(db.session, period_start, today)
        return reports

@blp.route("/metrics")
class ReportMetricsViews(MethodView):
    @blp.response(200, ReportSchema(many=True))
    def get(self):
        """List reports by key metrics: Power consumption, Peak usage, etc."""
        reports = db.session.query(
            Report.location,
            Report.consumption,
            Report.peak_usage_time,
            Report.cost,
            Report.cost_savings,
            Report.renewable_energy_utilization,
            Report.co2_emissions
        ).all()

        result = []
        for report in reports:
            result.append({
                'location': report[0],
                'power_consumption': report[1],
                'peak_usage_time': report[2],
                'power_cost': report[3],
                'cost_savings': report[4],
                'renewable_energy_utilization': report[5],
                'co2_emissions': report[6],
            })

        return jsonify(result)

@blp.route("/download")
class ReportDownloadViews(MethodView):
    @blp.arguments(ReportQueryArgsSchema, location="query")
    @blp.response(200)
    def get(self, args):
        """Download report as CSV based on custom period"""
        period_start = args.get('period_start')
        period_end = args.get('period_end')

        try:
            period_start = datetime.fromisoformat(period_start)
            period_end = datetime.fromisoformat(period_end)
        except ValueError:
            abort(400, message="Invalid date format")

        reports = get_general_report(db.session, period_start, period_end)

        # Generate CSV
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(['Location', 'Consumption', 'Cost', 'Period Start', 'Period End', 'CO2 Emissions', 'Peak Usage Time', 'Renewable Energy Utilization'])

        for report in reports:
            writer.writerow([report.location, report.consumption, report.cost, report.period_start, report.period_end, report.co2_emissions, report.peak_usage_time, report.renewable_energy_utilization])

        si.seek(0)

        return send_file(si, mimetype='text/csv', as_attachment=True, attachment_filename='report.csv')

@blp.route("/<int:report_id>")
class ReportByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, ReportSchema)
    def get(self, report_id):
        """Get report by ID"""
        report = Report.get_by_id(report_id)
        if report is None:
            abort(404, message="Report not found.")
        return report

    @blp.login_required
    @blp.etag
    @blp.arguments(ReportSchema)
    @blp.response(200, ReportSchema)
    def put(self, new_data, report_id):
        """Update an existing report"""
        report = Report.get_by_id(report_id)
        if report is None:
            abort(404, message="Report not found.")
        blp.check_etag(report, ReportSchema)
        report.update(**new_data)
        db.session.commit()
        return report

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, report_id):
        """Delete a report"""
        report = Report.get_by_id(report_id)
        if report is None:
            abort(404, message="Report not found.")
        blp.check_etag(report, ReportSchema)
        report.delete()
        db.session.commit()
