from flask.views import MethodView
from flask_smorest import abort
from bemserver_api import Blueprint
from bemserver_api.database import db
from bemserver_core.model import Team
from .schemas import TeamSchema, TeamQueryArgsSchema

blp = Blueprint(
    "Team",
    __name__,
    url_prefix="/teams",
    description="Operations on teams",
)

@blp.route("/")
class TeamViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TeamQueryArgsSchema, location="query")
    @blp.response(200, TeamSchema(many=True))
    def get(self, args):
        """List teams"""
        return Team.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TeamSchema)
    @blp.response(201, TeamSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new team"""
        item = Team.new(**new_item)
        db.session.commit()
        return item

@blp.route("/<int:item_id>")
class TeamByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TeamSchema)
    def get(self, item_id):
        """Get team by ID"""
        item = Team.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TeamSchema)
    @blp.response(200, TeamSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing team"""
        item = Team.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TeamSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a team"""
        item = Team.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TeamSchema)
        item.delete()
        db.session.commit()
 