
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, ForeignKey, PrimaryKeyConstraint


class CloudTables:

    def __init__(self):
        metadata_obj = MetaData()

        self.accounts = Table(
            "accounts",
            metadata_obj,
            Column("account_id", String(60), primary_key=True),
            Column("name", String(128), nullable=False),
            Column("owner", String(128)),
            #Column("type", String(10), nullable=False),
        )

        self.users = Table(
            "users",
            metadata_obj,
            Column("id", String(60), primary_key=True),
            Column("iam_id", String(128), nullable=False),
            Column("user_id", String(128), nullable=False),
            Column("account_id", String(60), ForeignKey("accounts.account_id")),
            Column("state", String(20), nullable=False),
        )

        self.serviceids = Table(
            "serviceids",
            metadata_obj,
            Column("id", String(60), primary_key=True),
            Column("iam_id", String(128), nullable=False),
            Column("name", String(128), nullable=False),
            Column("account_id", String(60), ForeignKey("accounts.account_id")),
        )

        self.trustedprofiles = Table(
            "trustedprofiles",
            metadata_obj,
            Column("id", String(60), primary_key=True),
            Column("iam_id", String(128), nullable=False),
            Column("name", String(128), nullable=False),
            Column("account_id", String(60), ForeignKey("accounts.account_id")),
        )

        self.trustedprofile_links = Table(
            "trustedprofile_links",
            metadata_obj,
            Column("id", String(60)),
            Column("cr_type", String(20), nullable=False),
            Column("tp_id", String(60), ForeignKey("trustedprofiles.id")),
            Column("link_crn", String(128), nullable=False),
            Column("link_namespace", String(128), nullable=True),
            Column("link_name", String(128), nullable=True),
        )

        self.access_groups = Table(
            "access_groups",
            metadata_obj,
            Column("id", String(60), primary_key=True),
            Column("name", String(128), nullable=False),
            Column("description", String(250)),
            Column("created_by_id", String(60), ForeignKey("users.iam_id")),
            Column("account_id", String(60), ForeignKey("accounts.account_id")),
        )

        self.access_group_members = Table(
            "access_group_members",
            metadata_obj,
            Column("iam_id", String(128), nullable=False),
            Column("group_id", String(128), nullable=False ),
            Column("type", String(20), nullable=False),
            Column("membership_type", String(20), nullable=False),
            PrimaryKeyConstraint("iam_id", "group_id", name="agm_pk"),
        )

        self.policies = Table(
            "policies",
            metadata_obj,
            Column("id", String(60), primary_key=True),
            Column("type", String(20), nullable=False),
            Column("state", String(20), nullable=False),
            Column("created_by_id", String(60)),
            Column("description", String(300)),
            Column("last_permit_at", String(30)),
            Column("last_permit_frequency", Integer),
            Column("account_id", String(60), ForeignKey("accounts.account_id")),
        )

        self.policy_roles = Table(
            "policy_roles",
            metadata_obj,
            Column("policy_id", String(60), ForeignKey("policies.id"), nullable=False),
            Column("role_id", String(128), nullable=False),
            Column("display_name", String(128)),
            PrimaryKeyConstraint("policy_id", "role_id", name="pr_pk"),
        )

        self.policy_resource_attributes = Table(
            "policy_resource_attributes",
            metadata_obj,
            Column("policy_id", String(60), ForeignKey("policies.id"), nullable=False),
            Column("resource_id", String(128), nullable=False),
            Column("name", String(128), nullable=False),
            Column("value", String(128), nullable=False),
            Column("operator", String(128)),
        )

        self.policy_subjects = Table(
            "policy_subjects",
            metadata_obj,
            Column("policy_id", String(60), ForeignKey("policies.id"), nullable=False),
            Column("subject_id", String(128), nullable=False),
            Column("name", String(128), nullable=False),
            Column("value", String(128), nullable=False),
        )


        self.resource_groups = Table(
            "resource_groups",
            metadata_obj,
            Column("resource_group_id", String(60), primary_key=True),
            Column("crn", String(128), nullable=False),
            Column("account_id", String(60), ForeignKey("accounts.account_id")),
            Column("name", String(128), nullable=False),
        )

        self.resource_service_instances = Table(
            "resource_service_instances",
            metadata_obj,
            Column("id", String(128), primary_key=True),
            Column("guid", String(128), nullable=False),
            Column("crn", String(128), nullable=False),
            Column("resource_group_id", String(60), ForeignKey("resource_groups.resource_group_id")),
            Column("account_id", String(60), ForeignKey("accounts.account_id")),
            Column("created_by", String(60), ForeignKey("users.iam_id")),
            Column("updated_by", String(60), ForeignKey("users.iam_id")),
            Column("name", String(128), nullable=False),
            Column("region_id", String(20), nullable=False),
        )

        self.metadata_obj=metadata_obj

    def createTables(self,engine):
        self.metadata_obj.create_all(engine)
