# Copyright 2016-2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

"""

Exporters for Jira.

In addition to its export job, an exporter has to:

* check in Jira if the record has been updated more recently than the
  last sync date and if yes, delay an import
* call the ``bind`` method of the binder to update the last sync date

"""

import logging
from contextlib import contextmanager


from odoo import _, fields, tools

from odoo.addons.component.core import AbstractComponent
from odoo.addons.queue_job.exception import RetryableJobError

from .mapper import iso8601_to_utc_datetime

_logger = logging.getLogger(__name__)


class F18BaseExporter(AbstractComponent):
    """Base exporter"""

    _name = "f18.base.exporter"
    _inherit = ["base.exporter", "f18.base"]
    _usage = "record.exporter"

    def __init__(self, work_context):
        super().__init__(work_context)
        self.binding = None
        self.external_id = None

    def _delay_import(self):
        """Schedule an import of the record.

        Adapt in the sub-classes when the model is not imported
        using ``import_record``.
        """
        # force is True because the sync_date will be more recent
        # so the import would be skipped if it was not forced
        assert self.external_id
        self.binding.import_record(self.backend_record, self.external_id, force=True)

    def _should_import(self):
        """Before the export, compare the update date
        in Jira and the last sync date in Odoo,
        if the former is more recent, schedule an import
        to not miss changes done in Jira.
        """
        assert self.binding
        if not self.external_id:
            return False
        sync = self.binder.sync_date(self.binding)
        if not sync:
            return True
        jira_updated = self.backend_adapter.read(self.external_id, fields=["updated"])[
            "fields"
        ]["updated"]

        sync_date = fields.Datetime.from_string(sync)
        jira_date = iso8601_to_utc_datetime(jira_updated)
        return sync_date < jira_date

    def _lock(self):
        """Lock the binding record.

        Lock the binding record so we are sure that only one export
        job is running for this record if concurrent jobs have to export the
        same record.

        When concurrent jobs try to export the same record, the first one
        will lock and proceed, the others will fail to lock and will be
        retried later.

        This behavior works also when the export becomes multilevel
        with :meth:`_export_dependencies`. Each level will set its own lock
        on the binding record it has to export.
        """
        self.component("record.locker").lock(self.binding)

    def run(self, binding, *args, **kwargs):
        """Run the synchronization

        :param binding: binding record to export
        """
        self.binding = binding

        if not self.binding.exists():
            return _("Record to export does no longer exist.")

        # prevent other jobs to export the same record
        # will be released on commit (or rollback)
        self._lock()

        self.external_id = self.binder.to_external(self.binding)
        result = self._run(*args, **kwargs)
        self.binder.bind(self.external_id, self.binding)
        # commit so we keep the external ID if several exports
        # are called and one of them fails
        if not tools.config["test_enable"]:
            self.env.cr.commit()  # pylint: disable=invalid-commit
        return result

    def _run(self, *args, **kwargs):
        """Flow of the synchronization, implemented in inherited classes"""
        raise NotImplementedError


