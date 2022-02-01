"""Timeseries by campaign routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_URL = "/timeseries/"
TIMESERIES_GROUPS_URL = "/timeseries_groups/"
TIMESERIES_GROUPS_BY_CAMPAIGNS_URL = "/timeseries_groups_by_campaigns/"


class TestTimeseriesGroupByCampaignsApi:
    def test_timeseries_groups_by_campaigns_api(
        self, app, users, timeseries, timeseries_groups, campaigns
    ):

        ts_1_id = timeseries[0]
        tg_1_id = timeseries_groups[0]
        tg_2_id = timeseries_groups[1]
        campaign_1_id, campaign_2_id = campaigns

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_GROUPS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            tgbc_1 = {"campaign_id": campaign_1_id, "timeseries_group_id": tg_1_id}
            ret = client.post(TIMESERIES_GROUPS_BY_CAMPAIGNS_URL, json=tgbc_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tgbc_1_id = ret_val.pop("id")
            tgbc_1_etag = ret.headers["ETag"]

            # POST violating unique constraint
            ret = client.post(TIMESERIES_GROUPS_BY_CAMPAIGNS_URL, json=tgbc_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_GROUPS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tgbc_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_GROUPS_BY_CAMPAIGNS_URL}{tgbc_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == tgbc_1_etag

            # POST
            tgbc_2 = {"campaign_id": campaign_2_id, "timeseries_group_id": tg_2_id}
            ret = client.post(TIMESERIES_GROUPS_BY_CAMPAIGNS_URL, json=tgbc_2)
            assert ret.status_code == 201
            ret_val = ret.json
            tgbc_2_id = ret_val.pop("id")

            # GET list (filtered)
            ret = client.get(
                TIMESERIES_GROUPS_BY_CAMPAIGNS_URL,
                query_string={"timeseries_group_id": tg_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tgbc_1_id
            assert ret_val[0]["timeseries_group_id"] == tg_1_id
            assert ret_val[0]["campaign_id"] == campaign_1_id
            ret = client.get(
                TIMESERIES_GROUPS_BY_CAMPAIGNS_URL,
                query_string={"campaign_id": campaign_2_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tgbc_2_id
            assert ret_val[0]["timeseries_group_id"] == tg_2_id
            assert ret_val[0]["campaign_id"] == campaign_2_id
            ret = client.get(
                TIMESERIES_GROUPS_BY_CAMPAIGNS_URL,
                query_string={
                    "timeseries_group_id": tg_1_id,
                    "campaign_id": campaign_2_id,
                },
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET TS list filtered by campaign
            ret = client.get(
                TIMESERIES_URL, query_string={"campaign_id": campaign_1_id}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(f"{TIMESERIES_GROUPS_BY_CAMPAIGNS_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE TS group violating fkey constraint
            ret = client.get(f"{TIMESERIES_GROUPS_URL}{tg_1_id}")
            tg_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{TIMESERIES_GROUPS_URL}{tg_1_id}", headers={"If-Match": tg_1_etag}
            )
            assert ret.status_code == 409

            # DELETE
            ret = client.delete(f"{TIMESERIES_GROUPS_BY_CAMPAIGNS_URL}{tgbc_1_id}")
            assert ret.status_code == 204
            ret = client.delete(f"{TIMESERIES_GROUPS_BY_CAMPAIGNS_URL}{tgbc_2_id}")
            assert ret.status_code == 204

            # GET list
            ret = client.get(TIMESERIES_GROUPS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_GROUPS_BY_CAMPAIGNS_URL}{tgbc_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("timeseries_groups_by_users")
    @pytest.mark.usefixtures("users_by_campaigns")
    def test_timeseries_groups_by_campaigns_as_user_api(
        self, app, users, timeseries_groups, campaigns, timeseries_groups_by_campaigns
    ):

        tg_1_id = timeseries_groups[0]
        tgbc_1_id = timeseries_groups_by_campaigns[0]
        tgbc_2_id = timeseries_groups_by_campaigns[1]
        campaign_1_id = campaigns[0]
        campaign_1_id = campaigns[0]

        creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_GROUPS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            assert len(ret.json) == 1
            assert ret.json[0]["id"] == tgbc_1_id
            assert ret.json[0]["campaign_id"] == campaign_1_id
            assert ret.json[0]["timeseries_group_id"] == tg_1_id

            # POST
            # We would get a 409 anyway since this association already exists.
            # But the 403 is triggered first.
            tgbc = {"campaign_id": campaign_1_id, "timeseries_group_id": tg_1_id}
            ret = client.post(TIMESERIES_GROUPS_BY_CAMPAIGNS_URL, json=tgbc)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_GROUPS_BY_CAMPAIGNS_URL}{tgbc_2_id}")
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_GROUPS_BY_CAMPAIGNS_URL}{tgbc_1_id}")
            assert ret.status_code == 200

            # DELETE
            ret = client.delete(f"{TIMESERIES_GROUPS_BY_CAMPAIGNS_URL}{tgbc_1_id}")
            assert ret.status_code == 403

    def test_timeseries_groups_by_campaigns_as_anonym_api(
        self, app, users, timeseries_groups, campaigns, timeseries_groups_by_campaigns
    ):

        tg_1_id = timeseries_groups[0]
        tgbc_1_id = timeseries_groups_by_campaigns[0]
        campaign_1_id = campaigns[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_GROUPS_BY_CAMPAIGNS_URL)
        assert ret.status_code == 401

        # POST
        tgbc = {"campaign_id": campaign_1_id, "timeseries_group_id": tg_1_id}
        ret = client.post(TIMESERIES_GROUPS_BY_CAMPAIGNS_URL, json=tgbc)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_GROUPS_BY_CAMPAIGNS_URL}{tgbc_1_id}")
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(f"{TIMESERIES_GROUPS_BY_CAMPAIGNS_URL}{tgbc_1_id}")
        assert ret.status_code == 401