import Api from "@/services/api";

class TriggerCaptureService {
  trigger() {
    return Api().put("/trigger");
  }
}

export default new TriggerCaptureService();
