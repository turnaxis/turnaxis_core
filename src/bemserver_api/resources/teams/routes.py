from datetime import date
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

        # Ensure only admins can add members
        if not current_user.is_admin:
            abort(403, message="Forbidden: Only admins can add members.")

        # Get the team by ID
        team = Team.get_by_id(team_id)
        if team is None:
            abort(404, message="Team not found")

        # Check if user already exists by email
        email = new_item.get("email")
        existing_user = db.session.query(User).filter_by(email=email).first()

        if existing_user:
            # if user exists, use their ID to add a new member
            item_user = existing_user
            print(f"User already exists: {existing_user}")
        else:
            # Create a new user if not found
            user_data = {
                "name": new_item.get("name"),  
                "email": email,  
            }
            item_user = User.new(**user_data)

            # Get and validate password
            password = new_item.get("password", None)
            if not password:
                abort(400, message="Password is required.")
            
            item_user.set_password(password)

            item_user.is_admin = False  # New member is not an admin by default
            item_user.is_active = True
            db.session.add(item_user)
            db.session.commit()

        print(item_user.id)

        # add the user to the members using ID
        new_member = Member(
            user_id=item_user.id,
            name=new_item.get("name"),
            email=email,
            password=item_user.password,
            permission_level="VIEWER",
            date_joined=date.today(),  
            team_id=team_id,
            
        )

        db.session.add(new_member)
        db.session.commit()

        return new_member

    

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
