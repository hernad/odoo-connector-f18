# Copyright 2016-2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

from odoo.addons.component.core import Component


class F18IssueType(models.Model):
    _name = "f18.issue.type"
    _inherit = "f18.binding"
    _description = "F18 Issue Type"

    name = fields.Char(required=True, readonly=True)
    description = fields.Char(readonly=True)
    backend_id = fields.Many2one(ondelete="cascade")

    def is_sync_for_project(self, project_binding):
        self.ensure_one()
        if not project_binding:
            return False
        return self in project_binding.sync_issue_type_ids

    def import_batch(self, backend, from_date=None, to_date=None):
        """Prepare a batch import of issue types from Jira

        from_date and to_date are ignored for issue types
        """
        with backend.work_on(self._name) as work:
            importer = work.component(usage="batch.importer")
            importer.run()



