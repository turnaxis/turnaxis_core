"""Overview for timeseries stats """

from textwrap import dedent

import flask

from flask_smorest import abort

from bemserver_core.database import db
from bemserver_core.exceptions import (
    BEMServerCoreDimensionalityError,
    TimeseriesDataIOError,
    TimeseriesNotFoundError,
)
from bemserver_core.input_output import tsdcsvio, tsdio, tsdjsonio
from bemserver_core.model import Campaign, Timeseries, TimeseriesDataState, UserGroupByCampaign, UserGroup, User,UserByUserGroup
from bemserver_core.authorization import get_current_user
from bemserver_core.database import db
from bemserver_api import Blueprint
from sqlalchemy import select
from .schemas import (
    TimeseriesDataDeleteByIDQueryArgsSchema,
    TimeseriesDataDeleteByNameQueryArgsSchema,
    TimeseriesDataGetByIDAggregateQueryArgsSchema,
    TimeseriesDataGetByIDQueryArgsSchema,
    TimeseriesDataGetByNameAggregateQueryArgsSchema,
    TimeseriesDataGetByNameQueryArgsSchema,
    TimeseriesDataGetStatsByIDBaseQueryArgsSchema,
    TimeseriesDataGetStatsByNameBaseQueryArgsSchema,
    TimeseriesDataPostQueryArgsSchema,
    TimeseriesDataStatsByIDSchema,
    TimeseriesDataStatsByNameSchema,
)

STATS_BY_ID_EXAMPLE = dedent(
    """\
    {
        "stats":
        {
            "1": {
                "first_timestamp": "2020-01-01T00:00:00+00:00",
                "last_timestamp": "2021-01-01T00:00:00+00:00",
                "count": 42,
                "min": 0.0,
                "max": 42.0,
                "avg": 12.0,
                "stddev": 4.2,
            },
            "2": {
                "first_timestamp": "2020-01-01T00:00:00+00:00",
                "last_timestamp": "2021-01-01T00:00:00+00:00",
                "count": 69,
                "min": 12.0,
                "max": 142.0,
                "avg": 69.0,
                "stddev": 6.9,
            },
        },
    }"""
)


STATS_BY_NAME_EXAMPLE = dedent(
    """\
    {
        "stats":
        {
            "Timeseries 1": {
                "first_timestamp": "2020-01-01T00:00:00+00:00",
                "last_timestamp": "2021-01-01T00:00:00+00:00",
                "count": 42,
                "min": 0.0,
                "max": 42.0,
                "avg": 12.0,
                "stddev": 4.2,
            },
            "Timeseries 2": {
                "first_timestamp": "2020-01-01T00:00:00+00:00",
                "last_timestamp": "2021-01-01T00:00:00+00:00",
                "count": 69,
                "min": 12.0,
                "max": 142.0,
                "avg": 69.0,
                "stddev": 6.9,
            },
        },
    }"""
)


PAYLOAD_BY_ID_JSON_EXAMPLE = dedent(
    """\
    {
        "1": {
            "2020-01-01T00:00:00+00:00": 0.1,
            "2020-01-01T10:00:00+00:00": 0.2,
            "2020-01-01T20:00:00+00:00": 0.3,
        },
        "2": {
            "2020-01-01T00:00:00+00:00": 1.1,
            "2020-01-01T10:00:00+00:00": 1.2,
            "2020-01-01T20:00:00+00:00": 1.3,
        },
        "3": {
            "2020-01-01T00:00:00+00:00": 2.1,
            "2020-01-01T10:00:00+00:00": 2.2,
            "2020-01-01T20:00:00+00:00": 2.3,
        },
    }"""
)

PAYLOAD_BY_ID_CSV_EXAMPLE = dedent(
    """\
    Datetime,1,2,3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3"""
)

PAYLOAD_BY_NAME_JSON_EXAMPLE = dedent(
    """\
    {
        "Timeseries 1": {
            "2020-01-01T00:00:00+00:00": 0.1,
            "2020-01-01T10:00:00+00:00": 0.2,
            "2020-01-01T20:00:00+00:00": 0.3,
        },
        "Timeseries 2": {
            "2020-01-01T00:00:00+00:00": 1.1,
            "2020-01-01T10:00:00+00:00": 1.2,
            "2020-01-01T20:00:00+00:00": 1.3,
        },
        "Timeseries 3": {
            "2020-01-01T00:00:00+00:00": 2.1,
            "2020-01-01T10:00:00+00:00": 2.2,
            "2020-01-01T20:00:00+00:00": 2.3,
        },
    }"""
)

PAYLOAD_BY_NAME_CSV_EXAMPLE = dedent(
    """\
    Datetime,Timeseries 1,Timeseries 2,Timeseries 3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3"""
)


def _get_data_state(data_state_id):
    return TimeseriesDataState.get_by_id(data_state_id) or abort(
        422, errors={"query": {"data_state": "Unknown data state ID"}}
    )


def _get_many_timeseries_by_id(timeseries_ids):
    try:
        return Timeseries.get_many_by_id(timeseries_ids)
    except TimeseriesNotFoundError as exc:
        abort(422, message=str(exc))


def _get_many_timeseries_by_name(campaign, timeseries_ids):
    try:
        return Timeseries.get_many_by_name(campaign, timeseries_ids)
    except TimeseriesNotFoundError as exc:
        abort(422, message=str(exc))


# blp = Blueprint(
#     "TimeseriesData",
#     __name__,
#     url_prefix="/timeseries_data",
#     description="Operations on timeseries data",
# )


blp = Blueprint(
    "TimeseriesDataForCampaignOverview",
    __name__,
    url_prefix="/overview/timeseries_data/organization/consumption",
    description="Operations on timeseries data for a given campaign",
)


@blp.route("/aggregate", methods=("GET",))
@blp.login_required
@blp.arguments(TimeseriesDataGetByNameAggregateQueryArgsSchema, location="query")
@blp.response(
    200, content_type="application/json", example=PAYLOAD_BY_NAME_JSON_EXAMPLE
)
@blp.alt_response(200, content_type="text/csv", example=PAYLOAD_BY_NAME_CSV_EXAMPLE)
def get_aggregate_for_campaign(args):
    """Get aggregated timeseries data for a given campaign

    Returns data in either JSON or CSV format.

    JSON: each key is a timestamp name as string. For each timeseries, values
    are passed a {timestamp: value} mappings.

    CSV: the first column is the timestamp as timezone aware datetime and each
    other column is a timeseries data. Column headers are timeseries names.
    """
    mime_type = flask.request.headers.get("Accept", "application/json")

    # campaign = Campaign.get_by_id(campaign_id) or abort(404)
    # timeseries = _get_many_timeseries_by_name(campaign, args["timeseries"])
    print(get_current_user())
    # query = select([Campaign.id]).select_from(
    # UserGroupByCampaign.__table__.join(
    #     UserGroup.__table__,
    #     UserGroupByCampaign.usergroup_id == UserGroup.id
    # ).join(
    #     Campaign.__table__,
    #     UserGroupByCampaign.campaign_id == Campaign.id
    # ).join(
    #     User.__table__,
    #     UserGroup.user_id == User.id
    # )
    # ).where(User.email == get_current_user.email)

    from sqlalchemy.orm import aliased
    from sqlalchemy import select

    # Build the query
    query = (
        db.session.query(Campaign)
        .join(UserGroupByCampaign, UserGroupByCampaign.campaign_id == Campaign.id)
        .join(UserGroup, UserGroupByCampaign.user_group_id == UserGroup.id)
        .join(UserByUserGroup, UserGroup.id == UserByUserGroup.user_group_id)
        .join(User, UserGroup.id == User.id)
        .filter(User.id == get_current_user().id)
    )

    # Execute the query and fetch results
    campaign_id = query.first().id


    # Execute the query
    # result = db.session.execute(query)
    # print(result)
    timeseries = Timeseries.get(campaign_id=campaign_id)
    print(timeseries)
    data_state = _get_data_state(args["data_state"])

    if mime_type == "text/csv":
        resp = tsdcsvio.export_csv_bucket(
            args["start_time"],
            args["end_time"],
            timeseries,
            data_state,
            args["bucket_width_value"],
            args["bucket_width_unit"],
            args["aggregation"],
            convert_to=args.get("convert_to"),
            timezone=args["timezone"],
            col_label="name",
        )
    else:
        resp = tsdjsonio.export_json_bucket_combined(
            args["start_time"],
            args["end_time"],
            timeseries,
            data_state,
            args["bucket_width_value"],
            args["bucket_width_unit"],
            args["aggregation"],
            convert_to=args.get("convert_to"),
            timezone=args["timezone"],
            col_label="name",
        )
        # print(resp)
    return flask.Response(resp, mimetype=mime_type)
