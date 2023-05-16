from odoo.addons.component.core import Component

class F18TypeBatchImporter(Component):
    """Import the Jira Issue Types

    For every id in in the list of issue types, a direct import is done.
    Import from a date
    """

    _name = "f18.issue.type.batch.importer"
    _inherit = "f18.direct.batch.importer"
    _apply_on = ["f18.issue.type"]

    def run(self):
        """Run the synchronization"""
        record_ids = self.backend_adapter.search()
        for record_id in record_ids:
            self._import_record(record_id)
