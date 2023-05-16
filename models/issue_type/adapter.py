class IssueTypeAdapter(Component):
    _name = "f18.issue.type.adapter"
    _inherit = ["jira.database.adapter"]
    _apply_on = ["f18.issue.type"]

    def read(self, id_):
        # pylint: disable=W8106
        with self.handle_404():
            return self.client.issue_type(id_).raw

    def search(self):
        issues = self.client.issue_types()
        return [issue.id for issue in issues]