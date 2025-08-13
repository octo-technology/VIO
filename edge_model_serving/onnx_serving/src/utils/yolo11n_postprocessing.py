import numpy as np
import cv2

# fct pour calculer score IOU
def compute_iou(box1, box2):
    x1, y1, x2, y2 = box1
    x1g, y1g, x2g, y2g = box2
    
    xi1, yi1 = max(x1, x1g), max(y1, y1g)
    xi2, yi2 = min(x2, x2g), min(y2, y2g)
    
    inter_width = max(0, xi2 - xi1)
    inter_height = max(0, yi2 - yi1)
    inter_area = inter_width * inter_height
    
    box1_area = (x2 - x1) * (y2 - y1)
    box2_area = (x2g - x1g) * (y2g - y1g)
    
    union_area = box1_area + box2_area - inter_area
    
    return inter_area / union_area if union_area > 0 else 0


# fct pour extraire les boîtes, scores et classes depuis les sorties YOLO ONNX
def yolo_extract_boxes_information(outputs, confidence_threshold=0.5):
    print(f"📌 Debug - outputs.shape: {np.array(outputs).shape}")  # ✅ Affiche la forme des outputs

    boxes = []
    scores = []
    class_ids = []
    
    for output in outputs:
        print(f"📌 Debug - output: {output}")  # ✅ Vérifie la structure de chaque ligne

        # Assurer que chaque sortie a bien 6 valeurs (x1, y1, x2, y2, conf, class_id)
        if len(output) < 6:
            print(f"⚠️ Warning : Une sortie YOLO ne contient que {len(output)} valeurs : {output}")
            continue  # Ignore cette sortie

        x1, y1, x2, y2, conf, class_id = output[:6]  # ✅ Prendre seulement les 6 premières valeurs

        if conf > confidence_threshold:
            boxes.append([int(x1), int(y1), int(x2), int(y2)])
            scores.append(float(conf))
            class_ids.append(int(class_id))
    
    return np.array(boxes), np.array(scores), np.array(class_ids)


# fct pour appliquer la suppression non maximale (NMS) aux boîtes détectées
def non_max_suppression(boxes, scores, class_ids, iou_threshold=0.3):
    indices = cv2.dnn.NMSBoxes(boxes.tolist(), scores.tolist(), 0.5, iou_threshold)
    filtered_boxes = []
    filtered_scores = []
    filtered_class_ids = []
    
    for i in indices.flatten():
        filtered_boxes.append(boxes[i])
        filtered_scores.append(scores[i])
        filtered_class_ids.append(class_ids[i])
    
    return np.array(filtered_boxes), np.array(filtered_scores), np.array(filtered_class_ids)

# 📌 Fonction pour calculer les "severities" (peut être modifié selon besoin)
def compute_severities(frame, boxes):
    severities = []
    for box in boxes:
        severity = np.random.uniform(0, 1)  # Exemple : générer un score aléatoire
        severities.append(severity)
    return severities
