def camera_id_been_pinged(metadata: dict, camera_id: str):
    if metadata == {} or metadata is None:
        return False
    camera_decisions = metadata.get("camera_decisions")
    camera_id_has_decision = camera_id in list(camera_decisions.keys())
    if camera_id_has_decision:
        return True
    return False
