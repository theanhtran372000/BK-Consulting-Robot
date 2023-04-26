import cv2

def draw_caption(image, point, caption):
    cv2.putText(
        image,
        caption,
        (point[0], point[1]),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 0),
        2,
    )
    cv2.putText(
        image,
        caption,
        (point[0], point[1]),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        1,
    )


def draw_rectangle(image, bbox, color=(255, 209, 0), thickness=3):
    cv2.rectangle(
        image,
        (bbox[0], bbox[1]),
        (bbox[0] + bbox[2], bbox[1] + bbox[3]),
        color,
        thickness,
    )


def draw_circle(image, point):
    cv2.circle(image, point, 7, (246, 250, 250), -1)
    cv2.circle(image, point, 2, (255, 209, 0), 2)
