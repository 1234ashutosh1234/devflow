from enum import StrEnum


class OrganizationRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


ROLE_LEVELS: dict[OrganizationRole, int] = {
    OrganizationRole.VIEWER: 10,
    OrganizationRole.DEVELOPER: 20,
    OrganizationRole.ADMIN: 30,
    OrganizationRole.OWNER: 40,
}