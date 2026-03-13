# Code Audit – VIO Edge Inspection Platform

## Architectural, Product & Market-Aligned Review

*Includes addendum: composable installation, camera-as-service, high-speed production, RAM disk, OpenTelemetry, native deployment, trigger layer revision (HTTP/gRPC/MQTT/OPC UA only, one active at a time), on-device training, model lifecycle, Data Studio.*

---

## 1. Global Architecture & Service Boundaries

### What Works Well

The codebase demonstrates a genuine commitment to **hexagonal architecture** in `edge_orchestrator`. The port-adapter split is well-executed: `domain/ports/` contains abstract interfaces, `infrastructure/adapters/` contains concrete implementations, and the domain models stay clean. The factory + manager pattern provides consistent lifecycle management across storage, cameras, rules, and model forwarders.

### Critical Issues

#### 1.1 — The Camera Config Is the Wrong Seam

The biggest structural smell is that `CameraConfig` carries `model_forwarder_config`. This means every camera is statically bound to a specific model at configuration time. An inspection station cannot dynamically assign models to cameras, run multiple models on the same image, or share a model across cameras without duplicating config.

This creates a **1:1:1 constraint** — one camera → one model → one prediction — that will fundamentally limit multi-model inspection scenarios (e.g., run a defect detector AND a presence checker on the same image).

The right seam should be: **pipeline step**, not camera. A camera captures an image; which models run on it, and in what order, is a pipeline concern.

#### 1.2 — Prediction Post-Processing is Split Across the Wrong Boundary

`ClassifModelForwarder` does image resize/normalize and argmax extraction. `ObjectDetectionModelForwarder` does NMS-style filtering client-side. Meanwhile, `tflite_serving` also does YOLO post-processing (NMS + severity) server-side. There is no consistent rule about what belongs where.

**The rule should be**: everything that is model-specific and output-format-specific belongs in the serving layer. The orchestrator should receive structured, typed predictions, not raw tensors or flat lists. Right now the orchestrator knows about model internals (number of output tensors, dimension ordering, normalization values), which breaks encapsulation entirely.

#### 1.3 — `ModelName` Enum is an Architectural Bottleneck

```python
class ModelName(str, Enum):
    fake_model = "fake_model"
    marker_quality_control = "marker_quality_control"
    ...
```

This enum means adding a new model requires a code change and a deploy. In an inspection platform, models should be runtime artifacts, not compile-time constants. The orchestrator should treat model names as opaque strings, discovered dynamically from the serving layer.

#### 1.4 — V1 vs V2 API Split is Undocumented and Risky

There are two router versions (`v1/`, `v2/`) with different contracts (notably, `/trigger` vs `/trigger_job`, and different binary response shapes). There is no explicit versioning strategy, no deprecation notices, and the interface still targets V1 exclusively. A client hitting V1 endpoints while V2 evolves will silently diverge.

#### 1.5 — Singleton Supervisor

`Supervisor` uses a `SingletonMeta` metaclass. In an async FastAPI context, this is a subtle footgun: the singleton carries mutable state across requests (`_camera_manager`, `_model_forwarder_manager`, etc.). If two concurrent triggers arrive during a config update, the state reset could affect both. The intended pattern here is likely **application-scoped service instances via lifespan**, not true singletons.

#### 1.6 — Service Communication Coupling

`edge_interface` calls `localhost:8000` (the orchestrator) directly from the browser. `edge_orchestrator` calls `http://edge_model_serving:8501` (Docker DNS). This means:
- The interface is **topology-aware**: it knows there is one orchestrator at a fixed address
- There is no internal API gateway or service mesh abstraction
- Changing ports or hostnames requires client code changes

#### 1.7 — Monolithic Stack Deployment

All edge services are deployed as a bundle. A user needing only MQTT trigger + one camera + one model still installs and runs the entire stack. This increases attack surface, memory footprint, and maintenance burden without delivering proportional value. True composability requires that services be individually selectable at both install time and runtime (enabled routers, loaded workers, active runtimes).

---

## 2. State of the Art & Market Alignment

### 2.1 — The Inference Protocol is Almost, But Not Quite, Standard

The serving URL pattern `/v1/models/{model_name}/versions/{model_version}:predict` is borrowed from TensorFlow Serving's REST API. But the payload and response shapes diverge significantly:

| Aspect | TF Serving Native | This Platform |
|---|---|---|
| Input key | `instances` or `inputs` | `inputs` |
| Input shape | Type-aware tensors | Raw Python list |
| Output (classif) | `{"predictions": [[0.1, 0.9]]}` | `{"outputs": [[0.1, 0.9]]}` |
| Output (detection) | Separate named tensors | Custom dict with `detection_boxes` etc. |
| Model type hint | N/A | `model_type: "yolo"` in payload |

The result is a **custom protocol that looks standard but isn't**, which is worse than a clearly custom protocol — it creates false confidence and breaks off-the-shelf clients.

### 2.2 — KServe V2 / Open Inference Protocol: Deliberate Partial Alignment

The **KServe V2 Inference Protocol** (also supported by Triton, OpenVINO Model Server, ONNX Runtime Server) has become the de facto standard for portable inference. Its key properties:

- **Model metadata endpoint** (`GET /v2/models/{model_name}`) describes input/output tensor shapes, dtypes, and names
- **Typed tensor inputs/outputs** — raw tensor I/O, no ambiguity about shape, dtype, or layout
- **Health and readiness endpoints** — standardized liveness/readiness
- **Version negotiation** — explicit model version support

**Deliberate choice: semantic predictions over raw tensors.** KServe V2 is tensor-in / tensor-out — post-processing (argmax, NMS, label mapping) stays client-side. For a domain-specific inspection platform, this is the wrong trade-off: it pushes model internals into the orchestrator, which is exactly what we want to avoid.

The current `tflite_serving` intentionally returns **typed semantic predictions** (`{prediction_type, label, probability}` or `{prediction_type, detected_objects}`). Post-processing is server-side, driven by `metadata.json`. The orchestrator receives clean domain objects, not tensors.

This is analogous to Triton's classification output extension — a semantic layer on top of the base tensor protocol.

**What we do align with:**
- Metadata endpoint concept (model shape, dtype, output type accessible via HTTP)
- Framework-independence principle (the orchestrator does not know it's TFLite)
- Model-as-runtime-artifact (model names are opaque strings, not code constants)

### 2.3 — `tflite_serving` → Inference Gateway

`ai_edge_litert` is a reasonable runtime for ARM/embedded. Auto-discovery of `.tflite` files from a directory is clean.

**✅ Resolved:** The output interpretation heuristic (3+ outputs = detection) has been removed. Each model now has a co-located `metadata.json` describing `output_type`, `normalization`, `class_names`, and input shape. Post-processing is driven by this metadata.

**✅ Resolved:** `ClassifModelForwarder` and `ObjectDetectionModelForwarder` have been merged into a single `ModelForwarder`. The orchestrator no longer knows about model internals.

**Future migration — `tflite_serving` becomes an inference gateway:**

The natural evolution of `tflite_serving` is not a multi-runtime monolith but a **smart proxy**: it receives raw bytes from the orchestrator, routes to the appropriate backend based on `metadata.json`, normalises the response to a standard semantic prediction, and returns it. The orchestrator is never modified regardless of which inference runtime is added.

```
edge_orchestrator
  → ModelForwarder ──raw bytes──▶ inference gateway (ex-tflite_serving)
                                    ↓ reads metadata.json: { "backend": "tflite_local" }
                                    IServingBackend
                                      → TfliteLocalBackend   (in-process, current)
                                      → TritonBackend        ──HTTP/gRPC──▶ Triton Server
                                      → OnnxServerBackend    ──HTTP──▶ ONNX Runtime Server
                                    ↓ post-process → semantic prediction
                                  ◀──── {"prediction_type": "class", "label": "OK", ...}
```

The `metadata.json` already carries `output_type` and `normalization`. Adding a `backend` field is the only config change needed to route a model to a different runtime:

```json
{ "output_type": "classification", "normalization": "mobilenet", "backend": "tflite_local" }
// tomorrow:
{ "output_type": "object_detection", "backend": "triton", "backend_url": "http://triton:8000" }
```

**Key property**: `backend` can be local (in-process, zero network overhead) or remote (a separate Triton/ONNX server). For local backends, the gateway calls the interpreter directly — no extra HTTP hop. For remote backends, it proxies.

The clean internal structure:

```
edge_model_serving/
  inference_gateway/
    domain/
      ports/
        i_serving_backend.py   ← run_inference(model_name, raw_bytes) → List[np.ndarray]
      post_processing/
        classification.py      ← argmax + label mapping (framework-agnostic)
        object_detection.py    ← NMS + bboxes (framework-agnostic)
        yolo.py
    infrastructure/
      adapters/
        tflite_local_backend.py   ← current tflite interpreter logic (in-process)
        triton_backend.py         ← POST /v2/models/{name}/infer, parse KServe V2 tensors
        onnx_server_backend.py    ← HTTP → ONNX Runtime Server
    api/
      api_routes.py               ← unchanged: always returns semantic typed predictions
```

**Do this refactor when:** a second inference runtime is actually needed. The current single-backend design is not technical debt — it is the correct scope for today.

---

## 3. Trigger Architecture & Extensibility

### Current State

The only trigger mechanism is `POST /api/v1/trigger` (or `/trigger_job` on V2). This is REST only, implemented directly as a FastAPI route handler. There is no abstraction layer between "something decided an inspection should happen" and "the inspection pipeline runs."

In the domain, an `Item` is created at trigger time — but the trigger itself is not modeled as a domain concept. There is no `InspectionRequest`, no `TriggerSource`, no event record.

### Why This Matters in Industrial Environments

Real inspection deployments trigger from:
- **PLC signals** over OPC UA, Modbus, or Profinet (most common in factory floors)
- **Conveyor belt sensors** via GPIO (high-frequency, sub-second latency requirements)
- **MQTT brokers** (IIoT standard, already deployed in most modern factories)
- **Camera push** (camera triggers inspection on motion or internal logic)
- **File drop** (when a machine saves an image, trigger analysis)
- **Scheduled jobs** (end-of-shift summary inspections)
- **Continuous video analysis** (streaming pipelines, not discrete trigger/capture)

Currently, integrating any of these requires modifying the core orchestration code. There is no plugin point.

### Revised Trigger Scope — Software Protocols Only

Physical signals (proximity sensors, camera hardware triggers) are always bridged to a software protocol before reaching vio-edge. This bridge is the customer's responsibility (PLC, lightweight Pi script, smart camera) and is out of scope.

```
Physical world              Bridge (out of scope)       vio-edge
─────────────────           ─────────────────────       ─────────────────
Proximity sensor        →   PLC / Pi script         →   MQTT or OPC UA
Camera HW trigger       →   Smart camera firmware   →   HTTP or gRPC
Operator UI             →   Web interface           →   HTTP
External system         →   Custom integration      →   gRPC
```

**Four supported trigger types — one active at a time:**

| Type | Package | Notes |
|---|---|---|
| HTTP/REST | core — always available | `POST /api/v1/trigger`, existing endpoint |
| gRPC | `vio-edge[grpc]` | Low-latency programmatic trigger — unary only (trigger → ack) |
| MQTT | `vio-edge[mqtt]` | Broker subscription (`aiomqtt`) |
| OPC UA | `vio-edge[opcua]` | Tag subscription on PLC (`asyncua`) |

`StationConfig.trigger` is a single object, not a list. Exactly one adapter runs per station. Switching trigger type → old adapter stops, new package installs if needed, new adapter starts. Hot-reload without process restart.

### Proposed Pattern: Trigger Adapter Architecture

```
Trigger source (one active)
  HTTP / gRPC / MQTT / OPC UA
          │
          ▼
   InspectionEvent              ← Domain concept
   trigger_source: str
   station_name: str
   timestamp: datetime
          │
          ▼
   Durable Event Queue          ← SQLite-backed (M3)
          │
          ▼
   Inspection Pipeline
   (Supervisor)
```

Implementation path:

1. Define `InspectionEvent` as a domain model (no behavior change)
2. Refactor REST trigger to emit `InspectionEvent` internally
3. `ITriggerAdapter` interface — `run(queue)` coroutine, `config_schema()` classmethod
4. MQTT adapter as optional extra (`vio-edge[mqtt]`)
5. OPC UA adapter as optional extra (`vio-edge[opcua]`)
6. gRPC adapter as optional extra (`vio-edge[grpc]`)

The orchestrator's inspection pipeline becomes **protocol-agnostic** — it only consumes `InspectionEvent` objects. GPIO is explicitly out of scope at the orchestrator level.

---

## 4. Camera as a First-Class Service

### Current State

The camera is not a service — it is an adapter invoked synchronously inside the inspection pipeline. The existing HLS streaming backend (`camera_server.py`) is an isolated POC and does not define the acquisition architecture. Cameras have no independent identity, health status, or lifecycle outside of an inspection cycle.

### The Gap

A camera in an industrial environment is not a passive peripheral. It may:
- Be electrically triggered by a proximity sensor or PLC signal — acting as a **trigger source**
- Push frames continuously into the pipeline (streaming mode) rather than responding to pull
- Have its own health state (focus drift, contamination, exposure saturation)
- Serve as a metadata source (capture timestamp, exposure settings, hardware ID)
- Be shared across multiple inspection pipelines

The current model — where `CameraConfig` lives inside `StationConfig` and cameras are instantiated per-inspection — cannot represent any of this.

### Target: Camera Service Contract — Two Acquisition Modes

Camera becomes an independent service with two distinct interaction modes. The mode is declared in the camera's `PipelineStep` config and determines the data flow direction.

#### Pull Mode — Orchestrator-Driven Acquisition

The orchestrator decides when to capture. A trigger event arrives → the worker dequeues it → the pipeline calls `POST /capture` on the camera service → receives an `ImageRef` → continues to inference.

```
External trigger → InspectionEvent → queue → worker
                                               │
                                               ▼
                                    POST /capture (per camera)
                                               │
                                               ▼
                                          ImageRef
                                               │
                                               ▼
                                         Inference
```

This is the current model and the default for most deployments: the orchestrator drives acquisition pace.

#### Push Mode — Camera-Driven Acquisition

The camera has its own trigger (hardware shutter signal, motion detection, internal timer). It captures the image autonomously and notifies the orchestrator with the pre-captured `ImageRef`. No `POST /capture` call is made.

The camera service calls a dedicated push endpoint on the orchestrator:

```
POST /api/v1/camera/push
  body: {
    "camera_id": "cam_1",
    "station_name": "ligne_1",
    "image_ref": { "uri": "file:///dev/shm/vio/item_42/cam_1.jpg", "captured_at": "...", "size_bytes": 98304 }
  }
  → 202 Accepted { "event_id": "..." }
```

This enqueues an `InspectionEvent` with the image already attached. The inspection worker checks `event.pre_captured_images` — if the camera's `ImageRef` is present, the acquisition step is skipped for that camera.

```python
class InspectionEvent:
    id: UUID
    station_name: str
    trigger_source: str          # "http" | "mqtt" | "grpc" | "opcua" | "camera_push"
    pre_captured_images: dict[str, ImageRef] = {}   # camera_id → ImageRef
    # pipeline skips POST /capture for cameras present in this dict
```

In push mode, the camera service is both trigger source and image provider. The camera service writes the image to the agreed ramdisk path before posting the push notification — the `file://` URI in the `ImageRef` is immediately resolvable by the orchestrator.

**Mode configuration in `PipelineStep`:**

```json
{ "camera_id": "cam_1", "mode": "pull", "capture_url": "http://cam-service:8081" }
{ "camera_id": "cam_1", "mode": "push" }
```

In push mode, `capture_url` is absent — the camera calls the orchestrator, not the reverse.

**One queue, one worker, both modes.** The only pipeline difference is whether the acquire step fires. Mixed-mode stations are possible (some cameras push, others are pulled within the same inspection).

#### Camera Service HTTP Contract

VIO defines the contract; users deploy their own implementation. Each hardware vendor has a proprietary SDK (Basler Pylon, Teledyne FLIR, Cognex VisionPro, IDS uEye). Bundling these creates licensing issues, bloats the base image, and forces platform-specific builds.

```
POST /capture                → ImageRef  (pull mode only)
GET  /health                 → { connected, focus_ok, last_capture_at }
GET  /metadata               → { resolution, fps_max, hardware_id, vendor }
```

Push-mode camera services do not implement `POST /capture`. They implement their own internal trigger loop and call `POST /api/v1/camera/push` on the orchestrator.

VIO may publish reference implementations (`vio-camera-usb`, `vio-camera-pi`) as separate installable packages.

### ImageRef — The Shared Domain Concept

Passing raw paths (`str`) between services creates implicit coupling to the filesystem layout. The right abstraction is `ImageRef`:

```python
class ImageRef:
    uri: str           # see URI resolution rules below
    camera_id: str
    captured_at: datetime
    size_bytes: int
```

**URI resolution — two deployment topologies:**

| Topology | `uri` value | How orchestrator resolves it |
|---|---|---|
| Same host (co-located) | `file:///dev/shm/vio/item_42/cam_1.jpg` | Read directly from filesystem |
| Remote host (separate machine) | `http://camera-service:8080/images/{id}` | HTTP GET to fetch bytes |

`POST /capture` always returns an `ImageRef`. The orchestrator checks the URI scheme and resolves accordingly via a `ImageRefResolver` port — one `FileSystemResolver`, one `HttpResolver`. This eliminates the implicit co-location requirement without changing the camera service contract.

The `file://` fast path (RAM disk, no network) is the default for single-host deployments. Remote URIs are transparent to the rest of the pipeline — they only affect the resolver, not inference or storage logic.

Tomorrow `uri` can be `s3://`, `minio://`, or `rtsp://` without changing any consumer beyond adding a resolver. The `ImageRef` is the stable domain currency for images — bytes only flow when a consumer explicitly resolves the URI.

### Async Capture & Parallelization — Pending Refactor

**Current state:** `HttpCamera.capture()` uses synchronous `httpx.post()`. `CameraManager.take_pictures()` calls cameras sequentially in a `for` loop. Since the inspection worker runs as an `asyncio` task, each blocking HTTP call stalls the entire event loop. For N cameras, acquisition latency is `sum(camera_i_latency)` instead of `max(camera_i_latency)`.

**Target:** `ICamera.capture()` → `async def capture()`, using `httpx.AsyncClient`. `CameraManager.take_pictures()` → `async def take_pictures()` with:

```python
images = await asyncio.gather(*[
    camera.capture() for camera in self._cameras.values()
], return_exceptions=True)
```

This is a cross-cutting change: `ICamera`, `HttpCamera`, `CameraManager`, `Supervisor`, `run_inspection_worker`, and all unit tests must be updated together. Interim mitigation: wrap sync calls in `asyncio.get_event_loop().run_in_executor(None, camera.capture)` to avoid blocking the loop without the full refactor.

**Do this before deploying to multi-camera stations** where sequential acquisition latency compounds.

### `start_listening` — Push Mode Backend Contract

`ICameraBackend.start_listening(out_dir, camera_id, on_frame)` in `edge_camera` is the internal push-mode loop for each backend. The contract:

- Runs until cancelled (caller cancels the `asyncio.Task`)
- Calls `on_frame(ImageRef)` for each captured frame — `on_frame` is an async callback that POSTs to `CAMERA_PUSH_URL`
- All blocking hardware calls (`cv2.VideoCapture.read()`, `Picamera2.capture_array()`, Basler `GrabOne()`) run in `asyncio.run_in_executor` to avoid blocking the event loop
- `finally` block in each backend releases hardware resources on cancellation
- `on_frame` swallows `Exception` (network failure) but not `asyncio.CancelledError` — clean shutdown propagates naturally

**Per-backend notes:**

| Backend | Blocking call | Executor pattern |
| --- | --- | --- |
| `OpenCvCameraBackend` | `cap.read()` | Opens capture once, loops `run_in_executor(cap.read)`, releases in `finally` |
| `Picamera2Backend` | `cam.capture_array()` | `cam.start()` once, loops `run_in_executor(capture_file)`, `stop()`+`close()` in `finally` |
| `BaslerCameraBackend` | `cam.GrabOne()` + PIL encode | `_grab_jpeg()` in executor per frame, camera opened/closed per call (stateless) |
| `FakeCameraBackend` | File read | Reads random image from directory, `asyncio.sleep(interval)` between frames |

**Known gap:** `start_listening` has no configurable frame rate limit or backpressure signal. If `on_frame` (POST to orchestrator) is slower than the camera frame rate, frames accumulate in memory. A bounded frame buffer or a drop-on-full strategy should be added before push mode is used at production frame rates.

---

## 5. High-Speed Production & Memory Management

### The Constraint

Production lines may operate at 5–50 parts per second. At these rates:
- Storing every image to disk is not viable (I/O bottleneck, storage exhaustion)
- Synchronous pipeline execution cannot keep up
- Cloud offload must be intelligent and bounded, not all-or-nothing

### RAM Disk Strategy

Store in-flight images in `/dev/shm/vio/` (tmpfs, RAM-backed):
- Pass file paths through the pipeline instead of serializing image bytes
- Eliminate encode/decode overhead between pipeline stages
- Automatic cleanup on process restart (tmpfs is volatile)
- Configurable retention: keep only KO images, sample OK at rate N, discard after TTL

```
Camera capture → /dev/shm/vio/{item_id}/{camera_id}.jpg
                       ↓
         Inference (reads from path, no copy)
                       ↓
         Decision: OK → discard after TTL
                   KO → move to persistent storage
                   SAMPLE → move to cloud offload queue
```

**Trade-off**: RAM disk is lost on power failure. For OK items that are discarded, this is acceptable. KO items and selected samples must be flushed to persistent storage before the TTL expires.

### Storage Service — Decoupled from the Orchestrator

The orchestrator's critical path is: acquire → infer → decide. Persisting images and metadata is **not** in this critical path and should not block it. Cloud uploads, compression, encryption, and retry logic have variable latency that must not propagate into inspection cycle time.

StorageService runs as a **separate process** on the same host, with the same decoupling philosophy as Camera Service and Model Serving: the orchestrator knows only the HTTP contract, not the implementation.

### StorageService HTTP Contract

```
POST /store
  body: {
    "item_id": "abc123",
    "image_refs": [{ "uri": "file:///dev/shm/vio/abc123/cam_1.jpg", "camera_id": "cam_1", ... }],
    "metadata_path": "/dev/shm/vio/abc123/metadata.json",
    "decision": "KO",
    "station_name": "ligne_1",
    "completed_at": "2026-03-12T14:23:00Z"
  }
  → 202 Accepted   ← StorageService acknowledged; handles async internally

GET /health
  → {
      "status": "ok",
      "cold_storage_used_bytes": 4294967296,
      "cold_storage_free_bytes": 21474836480,
      "upload_queue_depth": 3,
      "last_upload_at": "2026-03-12T14:22:58Z"
    }
```

The orchestrator calls `POST /store` fire-and-forget after each inspection completes and returns immediately on 202. The `IStoragePort` domain port wraps this call; an `HttpStorageAdapter` implements it. If no `storage_service_url` is configured, a `NullStorageAdapter` is used — valid for inference-only deployments.

### StorageService Internal Flow

```
POST /store received (202 returned immediately)
    │
    ▼ (internal async worker)
StorageService
    ├── uploads image + metadata.json → persistent storage (cloud or configured target)
    ├── on success: moves image + metadata.json → cold storage (/var/vio/items/{item_id}/)
    └── deletes item from ramdisk

StorageService background loop
    ├── monitors cold storage disk usage
    └── applies retention policy:
          OK items older than N days  → delete from cold storage (already in persistent storage)
          KO items                    → keep until explicit operator action
          disk pressure               → delete oldest OK items first
```

**Crash recovery is not needed for StorageService.** Data in cold storage has already been uploaded — it is a reliable local cache. Data still on ramdisk at crash time is lost; this is acceptable because ramdisk is explicitly ephemeral. The durability guarantee lives at the trigger layer (SQLite inspection queue), not at the storage layer.

No metadata database is introduced. The `metadata.json` per item is the complete record. The UI reads inspection history by listing cold storage items via the orchestrator API.

### StorageService Deployment

Launched as a separate subcommand with its own systemd unit:

```bash
vio-edge storage serve --port 8001 --config /etc/vio/storage.json
```

```ini
[Unit]
Description=VIO Storage Service
After=network.target

[Service]
ExecStart=/usr/local/bin/vio-edge storage serve --config /etc/vio/storage.json
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

StorageService is optional — the setup wizard only generates this unit if the user configures a storage target. The orchestrator `StationConfig` references it by URL: `"storage_service_url": "http://localhost:8001"`.

**Composability:**

| Deployment scenario | StorageService |
|---|---|
| Inference only, no storage | Not deployed — `NullStorageAdapter` in orchestrator |
| Local cold storage, no cloud | Deployed, no cloud target configured |
| Cold storage + cloud upload | Deployed, cloud adapter configured (S3, Azure, …) |
| Data gathering for training | Deployed, retention policy keeps all items |

**The existing `BinaryStorage` port** (`S3Adapter`, `AzureAdapter`) moves entirely into `StorageService`. The orchestrator stops importing storage adapters and only emits events via `IStoragePort`.

### Bounded Buffering

At high frame rates, the pipeline must implement backpressure:
- Trigger adapter feeds a bounded `asyncio.Queue` with a configurable max depth
- If the queue is full, the trigger is dropped (with a metric increment) rather than blocking
- This prevents memory exhaustion under burst load
- Queue depth is a primary operational metric

---

## 6. Durable Queue & Queue Technology

### Current State

`POST /trigger` launches a `BackgroundTask`. If the process restarts mid-inspection, the item is lost with no record, no retry, and no dead-letter queue.

### Recommendation: SQLite as Default

For single-node edge deployment, SQLite is the right default:
- No external service dependency
- ACID guarantees for queue operations
- Survives process restart
- Suitable for hundreds of items/second on modern ARM hardware

```sql
CREATE TABLE inspection_queue (
    id          TEXT PRIMARY KEY,
    event_json  TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending',  -- pending | running | done | failed
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    retry_count INTEGER NOT NULL DEFAULT 0
);
```

On startup: scan for `status = 'running'` rows (crashed mid-flight), reset to `pending` or mark `failed` based on age.

WAL mode (`PRAGMA journal_mode=WAL`) is recommended to reduce lock contention under concurrent reads.

The inspection queue is owned exclusively by the orchestrator worker. StorageService has no database — it operates on files directly. No cross-process SQLite contention exists.

### Optional: NATS for Multi-Node

If the deployment grows to multiple edge nodes sharing a queue, or if throughput exceeds SQLite's single-writer limits, NATS JetStream is the appropriate next step:
- Durable streams with consumer groups
- At-least-once delivery
- Sub-millisecond latency
- Adds operational complexity — should be opt-in, not the default

**Decision rule**: start with SQLite (separate files per process), migrate to NATS only when multi-node fan-out is required.

---

## 7. Edge Interface — Product Surface Audit

### Current Reality

The interface is a **thin technical frontend**, not an operational cockpit. Concretely:

| Capability | Present? | Notes |
|---|---|---|
| List inspection results | Yes | Basic table |
| View inspection images | Yes | Per item/camera |
| Trigger manual inspection | Yes | Single button |
| Switch configurations | Yes | Dropdown from API |
| Edit configurations | No | Read-only |
| Validate configurations | No | No schema enforcement |
| Model management | No | No awareness of available models |
| System health | No | No service status display |
| Camera live preview | Partial | Camera server exists but not integrated |
| Data gathering workflow | No | API exists, no UI |
| Error/failure display | Unclear | No dedicated error views |
| Role-based access | No | |
| Setup wizard | No | |

The camera streaming backend (`camera_server.py`) exists and serves HLS at `/camera/stream.m3u8` but is a separate service and not integrated into the main UI.

### Critical Product Issues

#### 7.1 — Configuration Management is a Black Box

To change a configuration, a user must:
1. Edit a JSON file on the filesystem of the edge device
2. Select it from the dropdown in the UI

There is no way to understand *what* a configuration does before activating it, no validation before activation, and no preview of the pipeline. For an industrial operator unfamiliar with JSON, this is a hard blocker.

#### 7.2 — Vue 2 + Vuetify 2 is End-of-Life

Vue 2 reached EOL in December 2023. Vuetify 2 is tied to Vue 2. This is active technical debt — security patches may not be available, and the ecosystem has moved to Vue 3 / Vuetify 3. A migration is necessary before the interface grows further.

#### 7.3 — No Feedback Loop on Inspection Quality

An operator cannot tell, from the interface, whether the system is performing well over time. There is no:
- Pass/fail rate over recent N items
- Confidence score trends
- Camera health indicators
- Model inference latency display

### Role-Based Views

Three roles cover the industrial reality. The UI gates sections by role; the API enforces the same roles server-side (UI gating alone is not a security control).

| Role | Who | Access |
|---|---|---|
| **Operator** | Line worker, daily user | Live status, results dashboard, camera previews, manual trigger. Read-only. |
| **Technician** | Line engineer, integrator | All Operator access + config editor, model browser, active config switching, Data Studio (labeling + training initiation). |
| **Admin** | IT, platform owner | All Technician access + user management, system config (storage targets, cloud credentials, network), OTA updates, security settings. |

Minimum viable implementation: API key per role tier, stored in `/etc/vio/auth.json`, enforced by middleware. Each role is strictly more permissive than the one above — no capability exists at Operator level that is absent at Technician level.

The setup wizard is always Technician-or-Admin only. The live inspection view (status bar, camera feed, results) is always available to Operators — they should never need to navigate away from it during production.

### Proposed Interface Architecture

Transform from **data browser** to **inspection cockpit**:

1. **Live status bar** — Always-visible top bar: service health indicators (orchestrator, model serving, storage), current config, inspection queue depth, recent pass/fail ratio, cold storage usage gauge, upload queue depth.

2. **Setup wizard** *(Technician / Admin)* — Guided flow: select use case → pick cameras → assign models → validate → activate.

3. **Configuration editor** *(Technician / Admin)* — Schema-aware JSON editor with inline validation against the Pydantic models.

4. **Camera preview panel** — Integrate existing HLS stream, show captured images alongside predictions.

5. **Results dashboard** — Time-series of OK/KO decisions, confidence distributions, anomaly flags. Each inspection result row shows a storage status badge: `↑ Uploaded` (in cloud + cold storage), `⏳ Pending` (awaiting StorageService), `⚠ Local only` (cold storage only, cloud unavailable), `✗ Evicted` (deleted per retention policy).

6. **Model browser** *(Technician / Admin)* — List models available in serving layer, show metadata (input shape, class names, version).

7. **System Health panel** — Per-service cards. StorageService card exposes:
   - Service reachability (Connected / Unreachable)
   - Cold storage disk gauge (used / free / total, warning at configurable threshold)
   - Items in cold storage by state (OK count, KO count, pending upload count)
   - Cloud target status and last successful upload timestamp
   - Upload throughput (MB/s)
   - Active retention policy summary (OK TTL, KO policy)

   Alert conditions surfaced as UI banners:
   - Cold storage > 80%: "Storage nearing capacity — oldest OK items will be deleted"
   - Upload queue depth > 50: "Storage backlog — check cloud connectivity"
   - StorageService unreachable: red indicator, inspection pipeline continues but no persistence guarantee shown

8. **User management** *(Admin only)* — Create/revoke API keys, assign roles, view access log.

---

## 8. AI Stack & Model Lifecycle

### Current State

Models are file-system artifacts placed in `/models/tflite/{model_name}/model.tflite`. There is no:
- Model version tracking beyond the directory name
- Metadata co-located with the model (input shape, normalization, output interpretation, class names)
- Rollback mechanism
- A/B testing or shadow mode
- Performance benchmarking at deployment time

Class names are stored in the orchestrator config (`camera_config.model_forwarder_config.class_names`), not with the model. If you update a model's output class order and forget to update all configs referencing it, you get silent misclassification.

### Recommendations

#### 9.1 — Model Metadata File (Quick Win)

Co-locate a `metadata.json` with each model:

```json
{
  "model_name": "marker_quality_control",
  "model_version": "1.2.0",
  "framework": "tflite",
  "input": {
    "shape": [1, 224, 224, 3],
    "dtype": "float32",
    "normalization": {"mean": 0.0, "std": 1.0, "scale": 127.5}
  },
  "output_type": "classification",
  "class_names": ["OK", "KO"],
  "created_at": "2024-01-15"
}
```

This moves model-specific knowledge from the orchestrator config into the model artifact itself. The serving layer reads this at startup and exposes it via the metadata endpoint.

#### 9.2 — Decoupled Model Forwarder

Once the serving layer exposes metadata, the orchestrator needs only one `ModelForwarder` implementation:

```python
class UniversalModelForwarder(IModelForwarder):
    async def forward(self, image: Image, config: ModelForwarderConfig) -> Prediction:
        metadata = await self._get_model_metadata(config.model_name)
        preprocessed = self._preprocess(image, metadata.input)
        raw_output = await self._predict(preprocessed, config)
        return self._postprocess(raw_output, metadata)
```

The three current forwarders (`ClassifModelForwarder`, `ObjectDetectionModelForwarder`, `SegmentationModelForwarder`) collapse into one.

#### 9.3 — Data Studio: Gathering, Labeling, Training

##### Foundation — shared by both training variants

vio-edge's existing data gathering mode captures images during production. A labeling interface in the web UI allows operators to tag images (OK / KO / defect class) without ML expertise — 200 images in ~20 minutes. The label is written into the item's existing `metadata.json` alongside capture timestamp, camera ID, and any inference results. No separate manifest file is needed — the dataset is the directory tree, and a training pipeline walks it reading each `metadata.json`. The labeling UI is the entry point to both training variants below.

##### Variante A — External Training

Images and metadata flow through `StorageService` as they are produced — no manual ZIP export. Two sub-variants:

**A1 — VIO Cloud Training:**
- `StorageService` continuously uploads labeled images + metadata to VIO Cloud Training as they are gathered
- Training is triggered from the web UI once the dataset is ready
- VIO Cloud trains the model, places it in the VIO Model Registry
- Local app is notified (webhook or polling): "model ready — accuracy 97.3%"
- Operator clicks "Download & activate" — model + `metadata.json` appear in the local models directory automatically

**A2 — Custom Training Factory (bring your own):**
- `StorageService` stores dataset locally on SSD or a configured storage backend
- vio-edge exposes `GET /api/v1/datasets/{id}` — returns dataset location and manifest path
- User runs their own training pipeline pointing at that location
- User uploads the resulting `.tflite` / `.onnx` + `metadata.json` via the model upload flow in the UI
- No integration work required from VIO beyond documenting the dataset manifest format

##### Variante B — On-Device Training (`vio-edge[train]`)

Available as an optional extra to keep the base binary lean.

**Framework:** `ai_edge_torch` (Google, successor to TFLite Model Maker) for transfer learning on classification and object detection. Backbone weights (MobileNetV2 ~14MB) are bundled or downloaded at first use.

**Hardware support:**

| Hardware | Backend | Estimated time (200 images, 20 epochs) |
|---|---|---|
| Raspberry Pi 5 | CPU | ~30–45 min |
| NVIDIA Jetson Orin | CUDA GPU | ~2–5 min |
| Apple Silicon Mac | Metal GPU | ~3–8 min (dev/test) |
| Any CUDA device | CUDA GPU | ~2–10 min |

**Flow:**
1. User selects a labeled dataset in Data Studio
2. Clicks "Train on this device" — hardware is detected and displayed
3. UI shows training progress (epoch, loss, val_accuracy via WebSocket)
4. On completion: `model.tflite` + `metadata.json` placed in the models directory automatically
5. User activates immediately — no upload, no download, no data leaves the factory network

**Data confidentiality:** production images cannot leave the site → Variante B eliminates the problem entirely.

**What the UI exposes:**

```
┌──────────────────────────────────────────────────────────┐
│  Data Studio                                             │
│                                                          │
│  Dataset "ligne_1" — 847 images                          │
│  ✓ OK: 623   ✓ KO: 201   ? Unlabeled: 23                │
│                                                          │
│  [ Continue labeling ]                                   │
│                                                          │
│  ─── Ready to train ────────────────────────────────── │
│                                                          │
│  [ Train on this device ]   [ Send to VIO Cloud ]       │
│    ~30 min · CPU only          ~5 min · GPU cloud        │
│    Data stays local            Requires internet         │
└──────────────────────────────────────────────────────────┘
```

---

## 9. Observability — OpenTelemetry Instrumentation

### Current State

No metrics, no distributed tracing, no structured logs. Operational visibility is limited to reading unstructured container stdout.

### Target: Full Inspection Trace

Every inspection must carry a **trace ID** that links all pipeline stages:

| Span | Measured |
|---|---|
| `trigger.received` → `queue.enqueued` | Trigger intake latency |
| `queue.dequeued` → `capture.start` | Queue wait time |
| `capture.start` → `capture.done` | Camera acquisition time (per camera) |
| `inference.start` → `inference.done` | Model inference latency (per model) |
| `rule.start` → `rule.done` | Rule evaluation time |
| `trigger.received` → `result.stored` | End-to-end inspection time |

Instrument with **OpenTelemetry** (OTLP exporter):
- Traces → Jaeger or Tempo
- Metrics → Prometheus (inspection count, pass/fail ratio, queue depth, inference p50/p95/p99)
- Logs → structured JSON with `trace_id` field for correlation

This is the single highest-leverage observability change — it makes every operational problem diagnosable without SSH.

---

## 10. Distributed Systems & Edge Robustness

### Critical Gaps

#### 11.1 — No Queue Between Trigger and Pipeline

`POST /trigger` runs the inspection pipeline as a `BackgroundTask`. If the API server restarts mid-inspection, the item is lost — no record, no retry. See section 7 for the SQLite queue recommendation.

#### 11.2 — Config Hot-Reload via Polling Flag

`ConfigManager.config_updated` is a flag that managers check on each request. This is a polling-based hot-reload with no atomicity guarantee. If a config update arrives mid-inspection, the item may be processed with a partially-applied new config.

**Recommendation**: Config changes should take effect only between inspection cycles. A read-write lock or a generation counter on the active config would prevent partial state.

#### 11.3 — No Crash Recovery for Items

`ItemState` tracks progress (TRIGGER → DONE), but this state is in-memory only. If the orchestrator crashes at `INFERENCE`, the item is in an indeterminate state. The metadata storage saves only *completed* items.

**Recommendation**: Persist `ItemState` transitions to the metadata store as they happen. On startup, scan for incomplete items and either reprocess or mark as FAILED.

#### 11.4 — No OTA Update Strategy

There is no documented strategy for updating model files, container images, or configurations on deployed edge devices. For a fleet in a factory, this requires physical access or manual SSH per device — not viable at scale.

---

## 11. Deployment — Native Binary, No Docker Required

### Target: Native Install as the Default

Docker is no longer the default deployment model. It adds overhead, requires a container runtime, and is unavailable or undesirable in many industrial contexts (locked-down industrial PCs, Raspberry Pi memory constraints, regulated environments). The hexagonal architecture already has no hard Docker dependencies — the change is packaging, not architecture.

### Installation Flow

A single curl command detects the OS and architecture, downloads the right pre-built binary from GitHub Releases, and installs it:

```bash
curl -fsSL https://get.vio-edge.io | sh
```

The installer script:

1. Detects OS (`uname -s`) and architecture (`uname -m`)
2. Maps to the correct binary: `linux-x86_64`, `linux-arm64`, `linux-armv7`, `macos-arm64`, `macos-x86_64`
3. Downloads from GitHub Releases (or a CDN mirror)
4. Installs to `/usr/local/bin/vio-edge` (Linux/Mac) or `%LOCALAPPDATA%\vio-edge\` (Windows)
5. On Linux: generates a systemd unit file (not activated yet)

The binary is built with PyInstaller — a self-contained executable embedding Python and the vio-edge core. No Python installation required on the target machine.

For Windows: a `.msi` installer available as a direct download from the GitHub Releases page.

### First Launch — Setup Wizard

```bash
vio-edge
```

No active config detected → starts a local HTTP server → opens `http://localhost:5173` in the default browser → displays the setup wizard. The terminal prints:

```
VIO Edge starting...
→ Open http://localhost:5173 to configure your system
  (your browser should open automatically)
```

The wizard collects: use case, trigger type (installs optional extras inline), camera service URLs, model selection, storage config. On completion it writes the station config and transitions to the operational cockpit — same URL, same server.

### Optional Extras — Installed On Demand

Optional trigger types and the training engine are installed as Python extras during the wizard, without the user touching a terminal:

```
vio-edge[grpc]   → grpcio
vio-edge[mqtt]   → aiomqtt
vio-edge[opcua]  → asyncua
vio-edge[train]  → ai_edge_torch + backbone weights
```

The wizard shows available/not-installed extras and installs them inline (progress shown in the browser). Switching trigger type later uninstalls the old extra and installs the new one.

### Process Management

On Linux, a systemd service is generated and activated after the wizard completes:

```ini
[Unit]
Description=VIO Edge Orchestrator
After=network.target

[Service]
ExecStart=/usr/local/bin/vio-edge serve --config /etc/vio/configs/
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Config lives in `/etc/vio/` (system install) or `~/.config/vio/` (user install). Models in `/var/lib/vio/models/` or `~/.local/share/vio/models/`.

### Docker — Optional, Community-Supported

Docker Compose support is retained for CI, development environments, and users who prefer it — but it is no longer the primary deployment path and is not required for production use. Maintaining Docker images becomes a community or secondary responsibility.

---

## 12. UX, DX & Adoption

### Developer Experience

The hexagonal architecture is genuinely DX-friendly — adding a new storage backend or camera type requires implementing one interface and registering it in the factory. This is well-designed.

However:
- No local development guide visible beyond example configs
- `FakeCamera` is excellent for local dev — this pattern should be documented prominently
- No test fixtures visible for model forwarders
- Config validation happens at startup but errors are not surfaced clearly to operators
- Two API versions with no migration guide or deprecation timeline

### Operator Experience (Time-to-First-Value)

To get a first inspection running today, an operator must:
1. Install Docker
2. Clone the repo
3. Place model files in the right directory structure
4. Write a JSON config referencing the right model names, camera types, storage paths
5. Run `make vio-edge-up`
6. Open the UI and trigger an inspection

Step 4 is the hard one. There is no guided setup, no config generator, no validation before runtime. An operator unfamiliar with the schema will hit opaque Python validation errors.

**Target**: A setup wizard in the UI that generates and validates configs, reducing operator friction to steps 1-2, then UI-guided for the rest.

---

## 13. Security & Operations

### Current Gaps

| Concern | Status |
|---|---|
| Authentication | None — all endpoints are open |
| Authorization | None |
| Secrets management | None visible — cloud credentials likely via env vars |
| HTTPS | Not configured — HTTP only |
| Container security | `privileged: true` on edge_orchestrator (broad) |
| Image signing | Not mentioned |
| Observability | No metrics, no tracing — unstructured logs only |
| Health endpoints | `/health/live` exists but no readiness/startup probes |

### Priority Recommendations

1. **Add `readiness` probe** — distinguish "service started" from "service ready to accept inspections" (models loaded, cameras initialized, config valid)
2. **Narrow privileged scope** — use `devices:` and specific capabilities instead of `privileged: true` where possible
3. **Add structured logging** — replace ad-hoc print/log with structured JSON logs with `trace_id` correlation field
4. **Metrics endpoint** — expose Prometheus-compatible metrics at `/metrics`: inspection count, pass/fail ratio, inference latency, queue depth

---

## Quick Wins

These can be done within days without architectural overhaul:

1. **Add `metadata.json` to each model directory** — move class names and normalization params out of orchestrator config. High impact, zero risk.

2. **Remove `ModelName` enum** — treat model names as opaque strings resolved at runtime by querying the serving layer. Unlocks runtime model addition without code deploys.

3. **Add `/v2/models/{model_name}` metadata endpoint to serving layer** — expose input shape, output type, class names. Foundation for the universal forwarder.

4. **Add a `readiness` probe** — `/health/ready` that checks model serving is reachable and at least one model is loaded.

5. **Add structured logging with OpenTelemetry** — emit JSON logs with `trace_id`. Zero behavior change, massive operational improvement.

6. **Migrate `edge_interface` to Vue 3 + Vuetify 3** — no functionality change, eliminates EOL dependency risk.

7. **Persist `ItemState` transitions** — write state changes to the metadata store as they happen. Enables crash recovery at near-zero cost.

8. **Document the V2 API and deprecation timeline for V1** — a `CHANGELOG.md` in `edge_orchestrator/` would prevent silent contract drift.

9. **Add RAM disk support for in-flight images** — mount `/dev/shm/vio/` and pass paths instead of bytes between pipeline stages.

---

## Mid-Term Improvement Roadmap

**Horizon: 1–3 months**

### M1 — Standard Inference Protocol (KServe V2 subset)

Align `edge_model_serving` with V2:
- Metadata: `GET /v2/models/{name}` returns input/output descriptions, normalization, class names
- Health: `GET /v2/health/ready`, `GET /v2/health/live`
- Inference: typed tensor payloads

Replace three model forwarders in the orchestrator with a single `V2ModelForwarder`.

**Trade-off**: More serving-side complexity, eliminates all model-specific logic from the orchestrator. Worth it.

### M2 — Trigger Plugin Architecture

Introduce `ITriggerAdapter` interface. Implement `RestTriggerAdapter` (core), `MqttTriggerAdapter` (`vio-edge[mqtt]`), `OpcUaTriggerAdapter` (`vio-edge[opcua]`), `GrpcTriggerAdapter` (`vio-edge[grpc]`). One adapter active at a time, started from lifespan based on `StationConfig.trigger`. Physical signals (GPIO, proximity sensors) are out of scope — they reach the orchestrator via the customer's existing bridge (PLC → MQTT/OPC UA).

### M3 — Durable SQLite Queue

Replace `BackgroundTask` with a SQLite-backed queue. Single worker coroutine drains the queue. On restart, incomplete items are reprocessed or flagged. Queue depth exposed as a metric.

### M4 — Camera Service Boundary

Define the full camera service contract with both acquisition modes:

- **Pull mode**: `POST /capture → ImageRef`, `GET /health`, `GET /metadata`. Replace the internal camera adapter with an `HttpCameraAdapter`. The pipeline step calls `POST /capture` and receives an `ImageRef`.
- **Push mode**: Camera service calls `POST /api/v1/camera/push` on the orchestrator with a pre-captured `ImageRef`. The orchestrator enqueues an `InspectionEvent` with `pre_captured_images` populated; the acquisition step is skipped for that camera. Mode is declared per camera in `PipelineStep` config: `"mode": "pull" | "push"`.

`InspectionEvent` gains a `pre_captured_images: dict[str, ImageRef]` field. Mixed-mode stations (some cameras push, others are pulled) are supported within the same inspection.

VIO provides reference implementations (`vio-camera-usb`, `vio-camera-pi`) as separate installable packages; the orchestrator only knows the contract.

### M_DS.1 — Labeling UI *(gate: data gathering mode must be stable)*

Add an image labeling interface to the web UI. Images captured in data gathering mode appear in a review queue. Operator clicks OK / KO / defect class. Label is written into the item's existing `metadata.json` — no separate format introduced.

**This milestone ships standalone** — it delivers immediate value (labeled dataset) even before any training integration exists. Do not couple it to M_DS.2 or M_DS.3.

### M_DS.2 — External Training Integration *(gate: M_DS.1 adopted, labeled datasets exist)*

- **A2 first (zero VIO infra required):** `GET /api/v1/datasets/{id}` returns the dataset root path and item count. User points their training pipeline at that path, reads `metadata.json` per item. Resulting `.tflite` / `.onnx` + model `metadata.json` uploaded via the model upload UI. The only integration contract is the `metadata.json` schema per item.
- **A1 second (requires VIO Cloud):** StorageService uploads labeled images + metadata to VIO Cloud Training as they are gathered. Training triggered from UI. Model placed in VIO Model Registry; local app notified via webhook/polling. Operator clicks "Download & activate."

Ship A2 before A1. A2 unblocks users with existing ML infrastructure at zero VIO cloud cost.

### M_DS.3 — On-Device Training *(gate: M_DS.1 adopted; independent of M_DS.2)*

Add `vio-edge[train]` extra. Transfer learning via `ai_edge_torch` on MobileNetV2 backbone (~14MB, downloaded at first use). GPU support: CUDA (Jetson, any CUDA device), Metal (Apple Silicon, dev/test). Training progress streamed to UI via WebSocket. Trained model + `metadata.json` auto-placed in models directory on completion.

Primary argument: production images cannot leave the factory network → on-device training eliminates the data-sovereignty problem entirely.

### ✅ M5 — Pipeline Step Abstraction *(resolved)*

`PipelineStep` model implemented. `StationConfig.pipeline_steps: Dict[str, PipelineStep]` replaces the previous 1:1:1 camera→model→rule coupling. See codebase.

### M6 — OpenTelemetry Instrumentation

Add OTEL SDK. Instrument all pipeline stages with spans. Export traces to Jaeger/Tempo, metrics to Prometheus. Add `trace_id` to all log lines.

### M7 — Interface Transformation

1. Migrate to Vue 3 + Vuetify 3
2. Add role-based access control (Operator / Technician / Admin); API key auth enforced server-side
3. Add system health status bar (all roles)
4. Integrate camera HLS stream in main UI (all roles)
5. Add results dashboard: pass/fail over time, confidence trend, queue depth, storage badges (all roles)
6. Add config editor with schema validation (Technician / Admin only)
7. Add user management panel (Admin only)

---

## Long-Term Target Architecture Vision

**Horizon: 6–12 months**

```
┌─────────────────────────────────────────────────────────────────┐
│                     EDGE NODE                                    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              CAMERA SERVICE  (separate process)          │    │
│  │  Pi Camera │ USB Camera │ GigE Vision │ IP Camera       │    │
│  │  pull: POST /capture → ImageRef │ GET /health           │    │
│  │  push: POST /api/v1/camera/push (→ orchestrator)        │    │
│  └──────┬─────────────────────────────────────┬────────────┘    │
│ pull ◀──┘ ImageRef (file:// or http://)        │ push: ImageRef  │
│  ┌───────────────────────────────────────┐     │                 │
│  │    TRIGGER ADAPTER (one active)       │     │                 │
│  │  HTTP (core) │ gRPC │ MQTT │ OPC UA  │     │                 │
│  │  Physical signals bridged externally  │     │                 │
│  └──────────────────┬────────────────────┘     │                 │
│                     │ InspectionEvent           │ InspectionEvent │
│  ┌──────────────────▼───────────────────────────▼─────────┐    │
│  │         DURABLE EVENT QUEUE  (SQLite WAL)                │    │
│  │         + RAM disk buffer  (/dev/shm/vio/)               │    │
│  └────────────────────────┬────────────────────────────────┘    │
│                           │                                      │
│  ┌────────────────────────▼────────────────────────────────┐    │
│  │           INSPECTION PIPELINE  (Orchestrator)            │    │
│  │  [Acquire? skip if push] → [Pipeline Steps] → [Rules]   │    │
│  │  [Item Rules] → [Emit Events]                            │    │
│  └──────┬───────────────────────────────────────┬──────────┘    │
│         │ V2 Inference Protocol                  │ POST /store   │
│  ┌──────▼──────────────────────────┐   ┌────────▼────────────┐  │
│  │  MODEL SERVING  (V2-Compatible) │   │  STORAGE SERVICE    │  │
│  │  TFLite │ ONNX │ OpenVINO       │   │  (separate process) │  │
│  │  metadata drives pre/post-proc  │   │  upload → cold stor │  │
│  └─────────────────────────────────┘   │  disk pressure mgmt │  │
│                                        └────────────┬─────────┘  │
│                                                     │ cloud upload│
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              OBSERVABILITY  (OpenTelemetry)              │    │
│  │   Structured logs │ Prometheus metrics │ OTLP traces    │    │
│  │   Trace ID on every inspection, every log line          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              EDGE INTERFACE  (Operational Cockpit)       │    │
│  │   Health │ Live Preview │ Results │ Config Editor        │    │
│  │   Model Browser │ Setup Wizard │ Storage Dashboard       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Deployment: native binary via curl | sh + systemd units        │
│  (Docker optional / community-supported)                        │
└────────────────────────────────┬────────────────────────────────┘
                                 │ Async sync (offline-tolerant)
┌────────────────────────────────▼────────────────────────────────┐
│                       CLOUD HUB (Optional)                       │
│   Model registry │ Fleet config push │ Aggregated analytics      │
│   OTA updates │ Central alerting │ Dataset collection           │
└─────────────────────────────────────────────────────────────────┘
```

### Key Properties of the Target State

- **Protocol-agnostic trigger layer** — HTTP, gRPC, MQTT, OPC UA; one active at a time; physical signals bridged externally (PLC, lightweight server)
- **V2-compatible inference protocol** — swap runtimes (TFLite → ONNX → OpenVINO) without touching the orchestrator
- **Model metadata drives all model-specific logic** — orchestrator has zero knowledge of normalization, class names, or output shape
- **Durable event queue** — no inspection is lost on crash or restart
- **Pipeline step model** — multi-model per camera, model chaining, conditional steps
- **Camera as an independent service** — HTTP contract (`POST /capture`, `GET /health`, `GET /metadata`); acquisition fully decoupled from orchestration; hardware-specific implementation is the operator's responsibility
- **Storage as an independent service** — `POST /store → 202 Accepted`; orchestrator fires-and-forgets; StorageService owns upload, cold storage, disk pressure management, and retention policy; `NullStorageAdapter` for inference-only deployments
- **High-speed production ready** — RAM disk buffering, bounded async queues, backpressure at ingestion
- **Data Studio** — operators label images from production, choose cloud or on-device training; no ML expertise required
- **Model lifecycle** — upload your own, download from VIO registry, or train on-device; `metadata.json` makes all model-specific config self-contained
- **Operational cockpit** — operators can fully manage the system without touching files or CLI
- **Structured observability** — every inspection carries a trace ID; latency, throughput, and quality are metered via OpenTelemetry
- **Native binary deployment** — `curl | sh` installs a self-contained binary; no Docker, no Python, no container runtime required; systemd for process management
- **Truly modular and composable** — install only what the use case requires (`vio-edge[mqtt]`, `vio-edge[train]`, etc.)

---

## Summary Risk Register

| Risk | Severity | Current State | Recommended Action |
|---|---|---|---|
| ~~Camera tightly coupled to model~~ | ~~High~~ | ✅ Resolved — `PipelineStep` model implemented | — |
| Pre/post-processing split across boundary | High | Argmax in orchestrator, NMS sometimes in serving | Model metadata + V2 protocol |
| `ModelName` enum blocks runtime model addition | Medium | Hardcoded enum | Treat as opaque string, resolve at runtime |
| No trigger abstraction | High | REST only, no plugin point | `ITriggerAdapter` — HTTP/gRPC/MQTT/OPC UA, one active at a time |
| No durable inspection queue | High | `BackgroundTask`, in-memory only | SQLite queue (M3) |
| No camera service abstraction | Medium | Camera as sync adapter in pipeline | Camera as external HTTP service; orchestrator only knows the contract |
| High-speed production not addressed | High | Synchronous pipeline, no buffering | RAM disk + bounded async queue |
| No OTA update strategy | High | Manual per-device update | Document + implement OTA path |
| Vue 2 EOL | Medium | Vue 2 + Vuetify 2 | Migrate to Vue 3 |
| No authentication | High | All endpoints open | Auth middleware (at minimum API key); role-based access: Operator / Technician / Admin |
| No observability | Medium | Unstructured logs only | OpenTelemetry (logs + metrics + traces) |
| Config stored as files, no validation UX | Medium | JSON files, no UI editor | Schema-aware config editor + setup wizard in UI |
| No model metadata co-location | Medium | Class names in orchestrator config | `metadata.json` per model |
| No crash recovery for in-flight items | High | Item state in-memory only | Persist state transitions |
| Docker mandatory | Medium | No native install path | Native binary via `curl \| sh`; Docker optional |
| Monolithic stack deployment | Medium | All services always deployed | Optional extras (`vio-edge[mqtt]`, `vio-edge[train]`, etc.) |
| No model training path | Medium | No data gathering → training loop | Data Studio: labeling + cloud training (A) + on-device training (B) |
