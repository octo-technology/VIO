from PIL import Image, ImageDraw, ImageFont


def filtering_items_that_have_predictions(metadata: dict, camera_id: str) -> bool:
    if metadata == {} or metadata is None:
        return False
    elif metadata["inferences"] == {}:
        return False
    for model_results in metadata["inferences"][camera_id].values():
        if model_results == 'NO_DECISION' or model_results == {}:
            return False
        for prediction in model_results.values():
            if "location" not in prediction:
                return False
    return True


def plot_predictions(img: Image, camera_id: str, metadata: dict) -> Image:
    if metadata["inferences"] == {}:
        return img
    camera_prediction_metadata = metadata["inferences"][camera_id]
    models = camera_prediction_metadata.keys()
    for model in models:
        detected_objects = camera_prediction_metadata[model].values()
        for detected_object in detected_objects:
            bbox = detected_object["location"]
            label = detected_object["label"]
            img = draw_bbox(img, bbox, label)

    return img


def draw_bbox(img, bbox, label):
    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Convert normalized coordinates to pixel values
    top_left_x = int(bbox[0] * width)
    top_left_y = int(bbox[1] * height)
    bottom_right_x = int(bbox[2] * width)
    bottom_right_y = int(bbox[3] * height)

    # Draw the bounding box
    draw.rectangle([top_left_x, top_left_y, bottom_right_x, bottom_right_y], outline="red", width=2)

    # Load a font
    font = ImageFont.load_default()

    # Calculate text size and position
    text_size = draw.textbbox((0, 0), label, font=font)[2:]
    text_x = top_left_x
    text_y = top_left_y - text_size[1] if top_left_y - text_size[1] > 0 else top_left_y

    # Draw the label background
    draw.rectangle([text_x, text_y, text_x + text_size[0], text_y + text_size[1]], fill="red")

    # Draw the label text
    draw.text((text_x, text_y), label, fill="white", font=font)

    return img