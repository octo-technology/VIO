def camera_id_been_pinged(metadata: dict, camera_id: str):
    if metadata == {} or metadata is None:
        return False
    camera_decisions = metadata.get("camera_decisions")
    if camera_id not in list(camera_decisions.keys()):
        return False
    camera_decision = camera_decisions[camera_id]
    if camera_decision == "NO_DECISION":
        return True
    return False
