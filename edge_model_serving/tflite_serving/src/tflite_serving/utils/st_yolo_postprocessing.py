import numpy as np
import tensorflow as tf

ANCHORS = np.array([
    0.0252, 0.06,
    0.0772, 0.1829,
    0.1696, 0.4167,
    0.3339, 0.6559,
    0.7226, 0.7348
]).reshape(-1, 2) # here https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/main/object_detection/pretrained_models/st_yolo_lc_v1/ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_lc_v1_256/st_yolo_lc_v1_256_config.yaml
NUM_CLASSES = 1


def tiny_yolo_v2_decode(feats, anchors, num_classes, input_shape, calc_loss=False):
    num_anchors = len(anchors)
    feats_dtype = feats.dtype

    anchors_tensors = tf.cast(tf.reshape(tf.constant(anchors), [1, 1, 1, num_anchors, 2]), feats_dtype)
    grid_shape = tf.shape(feats)[1:3]
    anchors_tensor = (anchors_tensors / tf.cast(input_shape[..., ::-1], feats_dtype)) * tf.cast(grid_shape[..., ::-1], feats_dtype)

    grid_y = tf.tile(tf.reshape(tf.range(0, grid_shape[0]), [-1, 1, 1, 1]), [1, grid_shape[1], 1, 1])
    grid_x = tf.tile(tf.reshape(tf.range(0, grid_shape[1]), [1, -1, 1, 1]), [grid_shape[0], 1, 1, 1])
    grid = tf.concat([grid_x, grid_y], axis=-1)
    grid = tf.cast(grid, feats_dtype)

    feats = tf.reshape(feats, [-1, grid_shape[0], grid_shape[1], num_anchors, num_classes + 5])

    box_xy = (tf.sigmoid(feats[..., :2]) + grid) / tf.cast(grid_shape[..., ::-1], feats_dtype)
    box_wh = tf.exp(feats[..., 2:4]) * anchors_tensor / tf.cast(grid_shape[..., ::-1], feats_dtype)
    box_confidence = tf.sigmoid(feats[..., 4:5])
    box_class_probs = tf.nn.softmax(feats[..., 5:])

    if calc_loss:
        return grid, feats, box_xy, box_wh
    return [box_xy, box_wh, box_confidence, box_class_probs]


def filter_boxes(my_boxes, boxes, box_confidence, box_class_probs, threshold=0.5):
    box_scores = box_confidence * box_class_probs
    box_classes = tf.argmax(box_scores, axis=-1)
    box_class_scores = tf.reduce_max(box_scores, axis=-1)
    prediction_mask = box_class_scores >= threshold
    boxes = tf.boolean_mask(boxes, prediction_mask)
    my_boxes = tf.boolean_mask(my_boxes, prediction_mask)
    scores = tf.boolean_mask(box_class_scores, prediction_mask)
    classes = tf.boolean_mask(box_classes, prediction_mask)
    return boxes, scores, classes, my_boxes


def process_boxes(box_xy, box_wh):
    box_mins = box_xy - (box_wh / 2.)
    box_maxes = box_xy + (box_wh / 2.)
    corners = tf.concat([
        box_mins[..., 1:2],  # y_min
        box_mins[..., 0:1],  # x_min
        box_maxes[..., 1:2],  # y_max
        box_maxes[..., 0:1],  # x_max
    ], axis=-1)
    centers = tf.concat([
        box_xy[..., 1:2],  # y
        box_xy[..., 0:1],  # x
        box_wh[..., 1:2],  # h
        box_wh[..., 0:1],  # w
    ], axis=-1)
    return corners, centers


def tiny_yolo_v2_nms(yolo_outputs, image_shape, max_boxes=30, score_threshold=0.5, iou_threshold=0.3, classes_ids=[0]):
    box_xy, box_wh, box_confidence, box_class_probs = yolo_outputs
    boxes, my_boxes = process_boxes(box_xy, box_wh)
    boxes, scores, classes, my_boxes = filter_boxes(my_boxes, boxes, box_confidence, box_class_probs,
                                                    threshold=score_threshold)

    height = image_shape[0]
    width = image_shape[1]
    image_dims = tf.stack([height, width, height, width])
    image_dims = tf.reshape(image_dims, [1, 4])
    image_dims = tf.cast(image_dims, dtype='float32')
    boxes = boxes * image_dims
    max_boxes_tensor = tf.Variable(max_boxes, dtype='int32')
    total_boxes = []
    total_scores = []
    total_classes = []
    total_my_boxes = []

    for c in classes_ids:
        mask = tf.equal(classes, c)
        s_classes = tf.boolean_mask(classes, mask)
        s_scores = tf.boolean_mask(scores, mask)
        s_boxes = tf.boolean_mask(boxes, mask)
        s_my_boxes = tf.boolean_mask(my_boxes, mask)

        nms_index = tf.image.non_max_suppression(
            s_boxes, s_scores, max_boxes_tensor, iou_threshold=iou_threshold)
        s_boxes = tf.gather(s_boxes, nms_index)
        s_scores = tf.gather(s_scores, nms_index)
        s_classes = tf.gather(s_classes, nms_index)
        s_my_boxes = tf.gather(s_my_boxes, nms_index)

        total_boxes.append(s_boxes)
        total_scores.append(s_scores)
        total_classes.append(s_classes)
        total_my_boxes.append(s_my_boxes)

    s_boxes = tf.concat(total_boxes, axis=0)
    s_my_boxes = tf.concat(total_my_boxes, axis=0)
    s_scores = tf.concat(total_scores, axis=0)
    s_classes = tf.concat(total_classes, axis=0)

    return s_boxes, s_scores, s_classes, s_my_boxes
