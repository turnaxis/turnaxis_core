"""Test authentication extension"""
import base64

from flask import jsonify

import pytest

from bemserver_api import Blueprint

from tests.common import TestConfig


class AuthTestConfig(TestConfig):
    AUTH_ENABLED = True


class TestAuthentication:

    @pytest.mark.parametrize(
        "app", (TestConfig, AuthTestConfig, ), indirect=True
    )
    @pytest.mark.usefixtures("users")
    def test_auth_login_required(self, app):

        active_user_creds = (
            base64.b64encode('active_user@test.com:@ctive'.encode())
            .decode()
        )
        inactive_user_creds = (
            base64.b64encode('inactive_user@test.com:in@ctive'.encode())
            .decode()
        )

        api = app.extensions['flask-smorest']['ext_obj']

        blp = Blueprint('AuthTest', __name__, url_prefix='/auth_test')

        @blp.route('/auth')
        @blp.login_required
        @blp.response(200)
        def auth():
            return None

        @blp.route('/no_auth')
        @blp.response(204)
        def no_auth():
            return None

        api.register_blueprint(blp)
        client = app.test_client()

        # Anonymous or inactive user
        for headers in (
            {},
            {'Authorization': 'Basic ' + inactive_user_creds},
        ):
            resp = client.get("/auth_test/auth", headers=headers)
            if app.config["AUTH_ENABLED"]:
                assert resp.status_code == 401
            else:
                assert resp.status_code == 200
            resp = client.get("/auth_test/no_auth", headers=headers)
            assert resp.status_code == 204

        # Active user
        for headers in (
            {'Authorization': 'Basic ' + active_user_creds},
        ):
            resp = client.get("/auth_test/auth", headers=headers)
            assert resp.status_code == 200
            resp = client.get("/auth_test/no_auth", headers=headers)
            assert resp.status_code == 204

        # Check OpenAPI spec
        spec = api.spec.to_dict()
        if app.config["AUTH_ENABLED"]:
            assert (
                spec["components"]["securitySchemes"]["BasicAuthentication"] ==
                {"type": "http", "scheme": "basic"}
            )
        else:
            assert (
                "BasicAuthentication" not in
                spec["components"].get("securitySchemes", {})
            )
        auth_spec = spec["paths"]["/auth_test/auth"]
        assert (
            auth_spec["get"]["responses"]["401"] ==
            {'$ref': '#/components/responses/UNAUTHORIZED'}
        )
        assert auth_spec["get"]["security"] == [{'BasicAuthentication': []}]
        no_auth_spec = spec["paths"]["/auth_test/no_auth"]
        assert "401" not in no_auth_spec["get"]["responses"]
        assert "security" not in no_auth_spec["get"]

    @pytest.mark.usefixtures("users")
    def test_auth_current_user(self, app):

        active_user_creds = (
            base64.b64encode('active_user@test.com:@ctive'.encode())
            .decode()
        )
        api = app.extensions['flask-smorest']['ext_obj']
        app.config["AUTH_ENABLED"] = True

        blp = Blueprint('AuthTest', __name__, url_prefix='/auth_test')

        @blp.route('/user')
        @blp.login_required
        @blp.response(200)
        def user():
            return jsonify(blp.current_user().name)

        api.register_blueprint(blp)
        client = app.test_client()

        # Active user
        headers = {'Authorization': 'Basic ' + active_user_creds}
        resp = client.get("/auth_test/user", headers=headers)
        assert resp.json == "Active"
