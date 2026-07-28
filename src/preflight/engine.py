# src/preflight/engine.py
from typing import Dict
from src.preflight.check import CHECK_REGISTRY
import requests
from src.preflight.sendemail import notify_developers_on_health_fail
from typing import Dict, Any, Callable, Tuple

import json
import os
from src.preflight.models import (
    PreflightReport,
    CheckResult,
    PreflightError,
)

import time

def run_preflight(
    checks: Dict[str, Dict],
    *,
    timeout_s: int = 8,
    verify_tls: bool = True,
    retries: int = 1,
    backoff_s: float = 1.2,
) -> PreflightReport:

    common = {
        "timeout_s": int(timeout_s),
        "verify_tls": bool(verify_tls),
        "retries": int(retries),
        "backoff_s": float(backoff_s),
    }

    results = []

    for name, cfg in checks.items():
        mandatory = bool(cfg.get("mandatory", True))
        enabled = bool(cfg.get("enabled", True))

        if not enabled:
            results.append(CheckResult(name, mandatory, False, "SKIP", 0, {}))
            continue

        fn = CHECK_REGISTRY.get(cfg.get("type"))

        if not fn:
            results.append(CheckResult(name, mandatory, True, "FAIL", 0,
                                       {"error": f"Unknown check type"}))
            continue

        status, latency, details = fn(cfg, common)
        results.append(CheckResult(name, mandatory, True, status, latency, details))

    overall = "OK"
    if any(r.mandatory and r.status == "FAIL" for r in results):
        overall = "FAIL"

    return PreflightReport(overall, int(time.time()*1000), results)


def run_preflight_or_raise(checks: Dict[str, Dict], **kwargs):
    report = run_preflight(checks, **kwargs)
    if report.overall != "OK":
        raise PreflightError(report.to_json())
    return report



def run_preflight_and_notify(
    checks: Dict[str, Dict[str, Any]],
    *,
    timeout_s: int = 8,
    verify_tls: bool = True,
    retries: int = 1,
    backoff_s: float = 1.2,
):
    report = run_preflight(
        checks,
        timeout_s=timeout_s,
        verify_tls=verify_tls,
        retries=retries,
        backoff_s=backoff_s,
    )

    # Send email if FAIL (but DO NOT raise)
    if report.overall != "OK":
        notify_developers_on_health_fail(report)

    return report
