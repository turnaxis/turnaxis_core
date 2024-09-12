from flask.views import MethodView
from flask_smorest import abort
from bemserver_api import Blueprint
from bemserver_api.database import db
from bemserver_core.model import Team, Member
from bemserver_core.model.users import User
from .schemas import MemberSchema, TeamSchema, TeamQueryArgsSchema
from bemserver_core.authorization import get_current_user

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
        return Team.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TeamSchema)
    @blp.response(201, TeamSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new team"""
        current_user = get_current_user()

        # Check if the current user is an admin
        if not current_user.is_admin:
            abort(403, message="Forbidden: Only admins can create teams.")

        # Create team without user_group_id requirement
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
        current_user = get_current_user()
        team = Team.get_by_id(team_id)

        user_data = {
            "name": new_item.get("name"),  
            "email": new_item.get("email"),  
        }

        item_user = User.new(**user_data)
        password = new_item.get("password", None)  # Get the password

        if not password:
            abort(400, message="Password is required.")

        item_user.set_password(password)  # Set the password for the user

        item_user.is_admin = False
        item_user.is_active = True
        db.session.add(item_user)
        db.session.commit()

        if team is None:
            abort(404, message="Team not found")

        # Ensure only admins can add members
        if not current_user.is_admin:
            abort(403, message="Forbidden: Only admins can add members.")

        print(current_user)

        # Set the default role to VIEWER
        new_item["team_id"] = team_id
        new_item["permission_level"] = "VIEWER"
        created_by=current_user.id
        item_user=item_user
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

@blp.route("/<int:team_id>/members/<int:member_id>")
class RemoveMemberView(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, team_id, member_id):
        """Remove a member from a team (Admin Only)"""
        current_user = get_current_user()
        team = Team.get_by_id(team_id)

        if team is None:
            abort(404, message="Team not found")

        # Ensure only admins can remove members
        if not current_user.is_admin:
            abort(403, message="Forbidden: Only admins can remove members.")

        member = Member.get_by_id(member_id)
        if member is None or member.team_id != team_id:
            abort(404, message="Member not found in this team")

        member.delete()
        db.session.commit()
 
@blp.route("/members/<int:member_id>/set-admin")
class SetAdminView(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, MemberSchema)
    def post(self, member_id):
        """Set a member as admin"""
        current_user = get_current_user()

        if not current_user.is_admin:
            abort(403, message="Only admins can assign other admins")

        member = Member.get_by_id(member_id)
        if member is None:
            abort(404, message="Member not found")
        
        member.permission_level = "ADMIN"
        db.session.commit()
        return member
