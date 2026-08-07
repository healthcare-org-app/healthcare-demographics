"""Kafka consumers for demographics-service.

One handler per subscribed topic. Handlers are best-effort logging plus
audit — services override this file to implement real cross-domain behavior.
"""
from __future__ import annotations

import logging

from healthcare_common.audit import emit_audit

log = logging.getLogger("demographics-service.consumers")


def register(svc) -> None:
    bus = svc.bus

    @bus.on("patient.updated")
    def _on_patient_updated(envelope: dict) -> None:
        log.info("demographics-service: received patient.updated id=%s", envelope.get("id"))
        emit_audit(bus, action="consume.patient.updated", actor="system:demographics-service",
                   target=None, details={"envelope_id": envelope.get("id")})

