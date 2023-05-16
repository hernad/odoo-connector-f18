from odoo.addons.component.core import AbstractComponent

class BatchImporter(AbstractComponent):
    """The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "f18.batch.importer"
    _inherit = ["base.importer", "f18.base"]
    _usage = "batch.importer"

    def run(self):
        """Run the synchronization, search all F18 records"""
        record_ids = self._search()
        for record_id in record_ids:
            self._import_record(record_id)

    def _search(self):
        return self.backend_adapter.search()

    def _import_record(self, record_id, **kwargs):
        """Import a record directly or delay the import of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError


class DirectBatchImporter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "f18.direct.batch.importer"
    _inherit = ["f18.batch.importer"]

    def _import_record(self, record_id, force=False, record=None):
        """Import the record directly"""
        self.model.import_record(
            self.backend_record, record_id, force=force, record=record
        )


class DelayedBatchImporter(AbstractComponent):
    """Delay import of the records"""

    _name = "f18.delayed.batch.importer"
    _inherit = ["f18.batch.importer"]

    def _import_record(self, record_id, force=False, record=None, **kwargs):
        """Delay the import of the records"""
        self.model.with_delay(**kwargs).import_record(
            self.backend_record, record_id, force=force, record=record
        )


class TimestampBatchImporter(AbstractComponent):
    """Batch Importer working with a f18.backend.timestamp.record

    It locks the timestamp to ensure no other job is working on it,
    and uses the latest timestamp value as reference for the search.

    The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "f18.timestamp.batch.importer"
    _inherit = ["base.importer", "f18.base"]
    _usage = "f18.batch.importer"

    def run(self, timestamp, force=False, **kwargs):
        """Run the synchronization using the timestamp"""
        original_timestamp_value = timestamp.last_timestamp
        if not timestamp._lock():
            self._handle_lock_failed(timestamp)

        next_timestamp_value, records = self._search(timestamp)

        timestamp._update_timestamp(next_timestamp_value)

        number = self._handle_records(records, force=force)

        return _("Batch from {} UTC to {} UTC generated {} imports").format(
            original_timestamp_value, next_timestamp_value, number
        )

    def _handle_records(self, records, force=False):
        """Handle the records to import and return the number handled"""
        for record_id in records:
            self._import_record(record_id, force=force)
        return len(records)

    def _handle_lock_failed(self, timestamp):
        _logger.warning("Failed to acquire timestamps %s", timestamp, exc_info=True)
        raise RetryableJobError(
            "Concurrent job / process already syncing",
            ignore_retry=True,
        )

    def _search(self, timestamp):
        """Return a tuple (next timestamp value, f18 record ids)"""
        until = datetime.now()

        parts = []
        if timestamp.last_timestamp:
            since = timestamp.last_timestamp
            from_date = since.strftime(JIRA_JQL_DATETIME_FORMAT)
            parts.append('updated >= "%s"' % from_date)
            to_date = until.strftime(JIRA_JQL_DATETIME_FORMAT)
            parts.append('updated <= "%s"' % to_date)

        next_timestamp = max(until - timedelta(seconds=IMPORT_DELTA), since)
        record_ids = self.backend_adapter.search(" and ".join(parts))
        return (next_timestamp, record_ids)

    def _import_record(self, record_id, force=False, record=None, **kwargs):
        """Delay the import of the records"""
        self.model.with_delay(**kwargs).import_record(
            self.backend_record,
            record_id,
            force=force,
            record=record,
        )
