import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import UserGroup
from bemserver_api import AutoSchema, Schema
from bemserver_api.extensions import ma_fields
from bemserver_core.model import Team
from bemserver_core.model.team import Member

class UserGroupSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = UserGroup

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))

class MemberSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Member

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field()
    permission_level = msa.auto_field(validate=ma.validate.OneOf(["ADMIN", "VIEWER"]))
    authorized_locations = msa.auto_field()
    email = ma.fields.Email(required=True)
    password = msa.auto_field(validate=ma.validate.Length(1, 80), load_only=True)
    date_joined = msa.auto_field()
    team_id = msa.auto_field()

class TeamSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Team

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    user_group_id = msa.auto_field(required=False)
    user_group = ma.fields.Nested(UserGroupSchema, dump_only=True)
    members = ma.fields.Nested(MemberSchema, many=True, dump_only=True)

class TeamQueryArgsSchema(Schema):
    sort = ma_fields.SortField(("name",))
    name = ma.fields.Str()
    user_group_id = ma.fields.Int(required=False)
 