"""Kafka consumers for demographics-service.

One handler per subscribed topic. Real handlers write to this service's own
database and/or publish follow-up events; stub handlers just log + audit.
"""
from __future__ import annotations

import logging

from psycopg.types.json import Json

from healthcare_common.audit import emit_audit

log = logging.getLogger("demographics-service.consumers")

TABLE = "demographics"


def register(svc) -> None:
    bus = svc.bus
    db = svc.db
    clients = svc.clients

    @bus.on("patient.updated")
    def _on_patient_updated(envelope: dict) -> None:
        data = envelope.get("data") or {}
        try:
                    pid = data.get("id")
                    if not pid: return
                    db.execute(f"INSERT INTO {TABLE} (data) VALUES (%s)",
                               (Json({"patient_id": pid, "snapshot": data,
                                      "captured_at": envelope.get("occurred_at")}),))
        except Exception as e:
            log.exception("demographics-service/patient.updated handler failed: %s", e)
        emit_audit(bus, action="consume.patient.updated", actor="system:demographics-service",
                   target=None, details={"envelope_id": envelope.get("id")})

