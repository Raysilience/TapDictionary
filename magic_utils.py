import cv2
import math

class BBox:
    def __init__(self, xmin=0, ymin=0, xmax=0, ymax=0):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
    def to_string(self):
        return "BBox:" + "\n\txmin: " + str(self.xmin) + "\t\tymin: " + str(self.ymin) + "\t\txmax: " + str(self.xmax) + "\t\tymax: " + str(self.ymax) + "\n"


def recognize_line(points):
    """
    Params:
        points: list of 2D tuples. each tuple represent a point of track
    Returns:
        (x1, y1), (x2, y2): representing start and end respectively
    """
    return points[0], points[-1]


def recognize_bbox(points):
    """
    Params:
        points: list of 2D tuples. each tuple represent a point of track
    Returns:
        BBox: type BBox. it represents the bounding box 
    """
    if not points or len(points) < 4:
        return None

    xmax = float('-inf')
    ymax = float('-inf')
    xmin = float('inf')
    ymin = float('inf')

    for point in points:
        xmax = max(point[0], xmax)
        ymax = max(point[1], ymax)
        xmin = min(point[0], xmin)
        ymin = min(point[1], ymin)
    
    return BBox(xmin, ymin, xmax, ymax)


def is_closed(points):
    if not points or len(points) < 3:
        return False
    start = points[0]
    end = points[-1]
    dist = math.sqrt((start[0]-end[0])**2 + (start[1]-end[1])**2)
    print("dist: ", dist)
    if dist > 40:
        return False
    else:
        return True