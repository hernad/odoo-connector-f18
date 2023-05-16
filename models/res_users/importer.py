from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.queue_job.exception import JobError


class UserImporter(Component):
    _name = "f18.res.users.importer"
    _inherit = ["f18.importer"]
    _apply_on = ["f18.res.users"]

    def _import(self, binding):
        record = self.external_record
        f18_key = self.external_id
        binder = self.binder_for("f18.res.users")
        user = binder.to_internal(f18_key, unwrap=True)
        if not user:
            email = record["emailAddress"]
            user = self.env["res.users"].search(
                ["|", ("login", "=", f18_key), ("email", "=", email)],
            )
            if len(user) > 1:
                raise JobError(
                    _(
                        "Several users found (%(login)s) for jira account"
                        "%(jira_key)s (%(email)s)."
                        " Please link it manually from the Odoo user's form.",
                        login=user.mapped("login"),
                        jira_key=jira_key,
                        email=email,
                    )
                )
            elif not user:
                raise JobError(
                    _(
                        "No user found for f18 account %(jira_key)s (%(email)s)."
                        " Please link it manually from the Odoo user's form.",
                        f18_key=f18_key,
                        email=email,
                    )
                )
            return user.link_with_external_source(backends=self.backend_record)