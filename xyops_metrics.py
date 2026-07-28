from prometheus_client import (
    CollectorRegistry,
    Gauge,
    Counter,
    Histogram,
    push_to_gateway,
    pushadd_to_gateway
)
import os
import time
import traceback
from urllib.error import HTTPError

# ---------------- CONFIG ----------------

PUSHGATEWAY_URL = os.getenv(
    "PUSHGATEWAY_URL", "http://10.9.46.42:31001"
)

JOB_NAME = "xyops_job"
SERVICE = "SoftwareProvisioning"

# ---------------- METRICS CLASS ----------------


class XYOpsMetrics:
    """
    FINAL production-safe metrics implementation.

    Design rules enforced:
    - Per-run metrics → Gauges / Histogram → push_to_gateway()
    - Lifetime metrics → Counters → pushadd_to_gateway()
    - DIFFERENT grouping keys to avoid deletion
    """

    def __init__(self):
        # 🔹 Registry for PER-RUN metrics (overwrite each run)
        self.run_registry = CollectorRegistry()

        # 🔹 Registry for LIFETIME metrics (accumulate forever)
        self.lifetime_registry = CollectorRegistry()

        self.pushgateway_url = PUSHGATEWAY_URL

        # ---------- PER-RUN METRICS ----------

        self.job_status = Gauge(
            "xyops_job_status",
            "XY OPS job status (1=success, 0=failure)",
            ["job", "service"],
            registry=self.run_registry
        )

        self.job_last_run_timestamp = Gauge(
            "xyops_job_last_run_timestamp",
            "Last time XY OPS job completed (unix timestamp)",
            ["job", "service"],
            registry=self.run_registry
        )

        self.job_duration = Histogram(
            "xyops_job_duration_seconds",
            "XY OPS job duration",
            ["job", "service"],
            registry=self.run_registry
        )

        self.total_mail_processed_run = Gauge(
            "xyops_total_mail_processed_run",
            "Total mails picked in this job run",
            ["job", "workflow"],
            registry=self.run_registry
        )

        self.mail_processed_run = Gauge(
            "xyops_mail_processed_run",
            "Tickets processed in this job run",
            ["job", "workflow"],
            registry=self.run_registry
        )

        self.mail_processed_failed_run = Gauge(
            "xyops_mail_processed_failed_run",
            "Tickets failed in this job run",
            ["job", "workflow"],
            registry=self.run_registry
        )

        # ---------- LIFETIME METRICS ----------

        self.mail_processed_total = Counter(
            "xyops_mail_processed_total",
            "Tickets processed across all runs",
            ["job", "workflow"],
            registry=self.lifetime_registry
        )

        self.mail_ignored_total = Counter(
            "xyops_mail_ignored_total",
            "Tickets failed across all runs",
            ["job", "workflow"],
            registry=self.lifetime_registry
        )

    # ---------------- PUSH LOGIC ----------------

    def push(self):
        """
        Push metrics to Pushgateway safely.

        CRITICAL:
        - Per-run metrics use scope=run
        - Lifetime counters use scope=lifetime
        """

        try:
            print("PUSHGATEWAY_URL =", self.pushgateway_url)

            # ✅ PER-RUN METRICS (REPLACE)
            push_to_gateway(
                self.pushgateway_url,
                job=JOB_NAME,
                grouping_key={
                    "service": SERVICE,
                    "scope": "run"
                },
                registry=self.run_registry,
                timeout=10
            )

            # ✅ LIFETIME COUNTERS (ADD)
            pushadd_to_gateway(
                self.pushgateway_url,
                job=JOB_NAME,
                grouping_key={
                    "service": SERVICE,
                    "scope": "lifetime"
                },
                registry=self.lifetime_registry,
                timeout=10
            )

            print("✅ Metrics pushed (run replaced, lifetime accumulated)")

        except HTTPError as e:
            print(f"❌ Pushgateway HTTPError: {e.code} {e.reason}")
            try:
                print(e.read().decode("utf-8", errors="replace"))
            except Exception:
                pass
            traceback.print_exc()

        except Exception:
            print("❌ Metrics push FAILED")
            traceback.print_exc()
