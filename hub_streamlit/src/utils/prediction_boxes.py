from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont


def filter_inferences_on_camera_id(
    camera_id: str, metadata: dict
) -> Optional[List[str]]:
    if metadata["inferences"] == {}:
        return None
    return metadata["inferences"][camera_id]


def plot_predictions(img: Image, camera_inferences_metadata: Dict[str, Dict]) -> Image:
    models_names = camera_inferences_metadata.keys()
    for model_name in models_names:
        detected_objects = camera_inferences_metadata[model_name].values()
        for detected_object in detected_objects:
            bbox = detected_object["location"]
            label = detected_object["label"]
            img = draw_bbox(img, bbox, label)
    return img


def draw_bbox(img: Image, bbox: tuple[float, float, float, float], label: str) -> Image:
    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Convert normalized coordinates to pixel values
    top_left_x = int(bbox[0] * width)
    top_left_y = int(bbox[1] * height)
    bottom_right_x = int(bbox[2] * width)
    bottom_right_y = int(bbox[3] * height)

    # Draw the bounding box
    draw.rectangle(
        [top_left_x, top_left_y, bottom_right_x, bottom_right_y], outline="red", width=2
    )

    # Load a font
    font = ImageFont.load_default()

    # Calculate text size and position
    text_size = draw.textbbox((0, 0), label, font=font)[2:]
    text_x = top_left_x
    text_y = top_left_y - text_size[1] if top_left_y - text_size[1] > 0 else top_left_y

    # Draw the label background
    draw.rectangle(
        [text_x, text_y, text_x + text_size[0], text_y + text_size[1]], fill="red"
    )

    # Draw the label text
    draw.text((text_x, text_y), label, fill="white", font=font)

    return img
