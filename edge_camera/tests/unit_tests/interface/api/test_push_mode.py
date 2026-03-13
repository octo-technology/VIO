"""Unit tests for push mode (_run_push_task and lifespan integration)."""

import asyncio
from unittest.mock import MagicMock, patch

from edge_camera.infrastructure.backends.fake_camera_backend import FakeCameraBackend
from edge_camera.interface.api.app import _run_push_task, create_app


async def test_push_task_posts_frame_to_url(tmp_path):
    backend = FakeCameraBackend()
    backend._frame_interval = 0.01

    posted = []

    async def fake_post(url, **kwargs):
        posted.append(kwargs.get("json"))
        if len(posted) >= 3:
            raise asyncio.CancelledError
        return MagicMock(status_code=200)

    with patch("httpx.AsyncClient.post", side_effect=fake_post):
        try:
            await _run_push_task(backend, "cam_1", "http://orchestrator/push", tmp_path)
        except asyncio.CancelledError:
            pass

    assert len(posted) >= 3
    for payload in posted:
        assert payload["camera_id"] == "cam_1"
        assert payload["uri"].startswith("file://")
        assert payload["size_bytes"] > 0


async def test_push_task_logs_warning_on_http_error(tmp_path, caplog):
    import logging

    backend = FakeCameraBackend()
    backend._frame_interval = 0.01

    call_count = 0

    async def failing_post(url, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count >= 3:
            raise asyncio.CancelledError
        raise OSError("connection refused")

    with patch("httpx.AsyncClient.post", side_effect=failing_post):
        with caplog.at_level(logging.WARNING, logger="edge_camera.interface.api.app"):
            try:
                await _run_push_task(backend, "cam_1", "http://orchestrator/push", tmp_path)
            except asyncio.CancelledError:
                pass

    assert any("Push failed" in r.message for r in caplog.records)


async def test_lifespan_starts_push_tasks_when_env_set(tmp_path, monkeypatch):
    monkeypatch.setenv("CAMERA_PUSH_URL", "http://orchestrator/frames")
    monkeypatch.setenv("CAMERA_OUTPUT_DIR", str(tmp_path))

    started = []

    async def fake_run_push_task(backend, camera_id, push_url, out_dir):
        started.append(camera_id)
        await asyncio.sleep(float("inf"))

    app = create_app()

    with patch("edge_camera.interface.api.app._run_push_task", side_effect=fake_run_push_task):
        async with app.router.lifespan_context(app):
            await asyncio.sleep(0.05)
            assert "cam_1" in started


async def test_lifespan_no_push_tasks_when_env_not_set(tmp_path, monkeypatch):
    monkeypatch.delenv("CAMERA_PUSH_URL", raising=False)

    started = []

    async def fake_run_push_task(*args, **kwargs):
        started.append(True)
        await asyncio.sleep(float("inf"))

    app = create_app()

    with patch("edge_camera.interface.api.app._run_push_task", side_effect=fake_run_push_task):
        async with app.router.lifespan_context(app):
            await asyncio.sleep(0.05)
            assert started == []
