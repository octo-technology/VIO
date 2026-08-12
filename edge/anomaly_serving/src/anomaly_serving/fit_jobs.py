"""Background memory-bank fit jobs with pollable progress.

Fitting can take from seconds to minutes, so a fit request returns a job id
immediately and the work runs off the request. The dashboard polls the job to
show progress. Jobs are kept in memory on ``app.state`` — a single-process edge
service with a handful of models needs nothing heavier, and a restart re-reads
the persisted banks anyway.

The blocking feature extraction runs in a worker thread so the event loop stays
free to answer progress polls while a fit is in flight.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from pathlib import Path
from typing import Any, Dict

import torch
from starlette.concurrency import run_in_threadpool

from anomaly_serving.preprocessing import preprocess_bytes
from anomaly_serving.rad_model.rad import RAD
from anomaly_serving.reference_bank import append_reference_images, save_checkpoint

logger = logging.getLogger(__name__)

STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

_JOB_PUBLIC_FIELDS = ("job_id", "model_name", "status", "processed", "total", "bank_size", "error")


def init_job_state(app: Any) -> None:
    """Initialise the in-memory job registry on app state (idempotent)."""
    if not hasattr(app.state, "fit_jobs") or app.state.fit_jobs is None:
        app.state.fit_jobs = {}
    if not hasattr(app.state, "fitting_models") or app.state.fitting_models is None:
        app.state.fitting_models = set()


def serialize_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """Project a job onto the fields exposed by the API."""
    return {field: job[field] for field in _JOB_PUBLIC_FIELDS}


def start_fit_job(
    app: Any,
    model_name: str,
    model: RAD,
    images_bytes: list[bytes],
    resize: int,
    ckpt_path: Path,
) -> Dict[str, Any]:
    """Register a fit job and schedule it on the running event loop."""
    init_job_state(app)
    job: Dict[str, Any] = {
        "job_id": uuid.uuid4().hex,
        "model_name": model_name,
        "status": STATUS_PENDING,
        "processed": 0,
        "total": len(images_bytes),
        "bank_size": None,
        "error": None,
    }
    app.state.fit_jobs[job["job_id"]] = job
    app.state.fitting_models.add(model_name)
    asyncio.create_task(_run_fit_job(app, model, images_bytes, resize, ckpt_path, job))
    return job


async def _run_fit_job(
    app: Any,
    model: RAD,
    images_bytes: list[bytes],
    resize: int,
    ckpt_path: Path,
    job: Dict[str, Any],
) -> None:
    job["status"] = STATUS_RUNNING
    try:
        job["bank_size"] = await run_in_threadpool(_fit, model, images_bytes, resize, ckpt_path, job)
        job["status"] = STATUS_COMPLETED
    except Exception as exc:
        # A failed fit is surfaced to the client through the job's error field
        # rather than crashing the background task.
        logger.exception("Fit job %s for model '%s' failed", job["job_id"], job["model_name"])
        job["error"] = str(exc)
        job["status"] = STATUS_FAILED
    finally:
        app.state.fitting_models.discard(job["model_name"])


def _fit(
    model: RAD,
    images_bytes: list[bytes],
    resize: int,
    ckpt_path: Path,
    job: Dict[str, Any],
) -> int:
    """Decode, fit, and persist — the blocking body run in a worker thread.

    Decoding happens up front so a bad image fails the job before the bank is
    touched; the bank is only ever mutated once, with a full valid batch.
    """
    tensors = [preprocess_bytes(data, resize) for data in images_bytes]
    images = torch.cat(tensors, dim=0)

    def on_progress(processed: int) -> None:
        job["processed"] = processed

    bank_size = append_reference_images(model, images, progress_cb=on_progress)
    save_checkpoint(model, ckpt_path)
    return bank_size
