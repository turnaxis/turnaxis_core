from flask.views import MethodView
from flask_smorest import abort
from bemserver_api import Blueprint
from bemserver_api.database import db
from bemserver_core.model import Team, Member
from .schemas import MemberSchema, TeamSchema, TeamQueryArgsSchema

blp = Blueprint(
    "Team",
    __name__,
    url_prefix="/api/v1/teams",
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
        # query = Team.query
        # if "name" in args:
        #     query = query.filter(Team.name == args["name"])
        # if "user_group_id" in args:
        #     query = query.filter(Team.user_group_id == args["user_group_id"])
        # return query.all()
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
        

@blp.route("/<int:team_id>/members")
class MemberViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, MemberSchema(many=True))
    def get(self, team_id):
        """List all members of a specific team"""
        team = Team.get_by_id(team_id)
        if team is None:
            abort(404, message="Team not found")
        members = db.session.query(Member).filter_by(team_id=team_id).all()

        return members

    @blp.login_required
    @blp.etag
    @blp.arguments(MemberSchema)
    @blp.response(201, MemberSchema)
    @blp.catch_integrity_error
    def post(self, new_item, team_id):
        """Add a member to a team"""
        team = Team.get_by_id(team_id)
        if team is None:
            abort(404, message="Team not found")
        new_item["team_id"] = team_id
        item = Member.new(**new_item)
        db.session.commit()
        return item

    

@blp.route("/members/<int:member_id>")
class MemberByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, MemberSchema)
    def get(self, member_id):
        """Get member by ID"""
        member = Member.get_by_id(member_id)
        if member is None:
            abort(404)
        return member

    @blp.login_required
    @blp.etag
    @blp.arguments(MemberSchema)
    @blp.response(200, MemberSchema)
    @blp.catch_integrity_error
    def put(self, new_item, member_id):
        """Update a member by ID"""
        member = Member.get_by_id(member_id)
        if member is None:
            abort(404)
        blp.check_etag(member, MemberSchema)
        member.update(**new_item)
        db.session.commit()
        return member

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, member_id):
        """Delete a member"""
        member = Member.get_by_id(member_id)
        if member is None:
            abort(404)
        blp.check_etag(member, MemberSchema)
        member.delete()
        db.session.commit()
 
@blp.route("/members/<int:member_id>/set-admin")
class SetAdminView(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, MemberSchema)
    def post(self, member_id):
        """Set a member as admin"""
        member = Member.get_by_id(member_id)
        if member is None:
            abort(404, message="Member not found")
        
        member.permission_level = "ADMIN"
        db.session.commit()
        return member
