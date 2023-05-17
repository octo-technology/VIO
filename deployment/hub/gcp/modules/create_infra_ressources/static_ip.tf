resource "google_compute_global_address" "edge-model-serving" {
  name = "tf-vio-edge-model-serving"
}

resource "google_compute_global_address" "edge-orchestrator" {
  name = "tf-vio-edge-orchestrator"
}

resource "google_compute_global_address" "edge-interface" {
  name = "tf-vio-edge-interface"
}