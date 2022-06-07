import pytest
from invenio_records_resources.services.errors import PermissionDeniedError


@pytest.fixture(scope="function")
def groups_disabled(app):
    app.config["COMMUNITIES_GROUPS_ENABLED"] = False
    yield
    app.config["COMMUNITIES_GROUPS_ENABLED"] = True


def test_invite_member_with_groups_disabled(
    member_service, community, owner, new_user, db, groups_disabled
):
    """Invite a user when the groups are disabled."""
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
    }
    member_service.invite(owner.identity, community._record.id, data)


@pytest.mark.parametrize(
    "actor,role",
    [
        ("owner", "owner"),
        ("owner", "manager"),
        ("owner", "curator"),
        ("owner", "reader"),
        ("manager", "manager"),
        ("manager", "curator"),
        ("manager", "reader"),
    ],
)
def test_add_member_with_groups_disabled(
    member_service, community, members, group, actor, role, db, groups_disabled
):
    """Test that the COMMUNITIES_GROUPS_ENABLED flag allows/forbids to add
    members.
    """
    data = {
        "members": [{"type": "group", "id": group.name}],
        "role": role,
    }

    assert pytest.raises(
        PermissionDeniedError,
        member_service.add,
        members[actor].identity,
        community._record.id,
        data,
    )
