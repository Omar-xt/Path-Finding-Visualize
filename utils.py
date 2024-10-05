from collections.abc import Sequence
from dataclasses import dataclass
from math import atan, dist, radians, cos, sin


class NamedMutableSequence(Sequence):
    __slots__ = ()

    def __init__(self, *a, **kw):
        slots = self.__slots__
        for k in slots:
            setattr(self, k, kw.get(k))

        if a:
            for k, v in zip(slots, a):
                setattr(self, k, v)

    def __str__(self):
        clsname = self.__class__.__name__
        values = ", ".join("%s=%r" % (k, getattr(self, k)) for k in self.__slots__)
        return "%s(%s)" % (clsname, values)

    __repr__ = __str__

    def __getitem__(self, item):
        return getattr(self, self.__slots__[item])

    def __setitem__(self, item, value):
        return setattr(self, self.__slots__[item], value)

    def __len__(self):
        return len(self.__slots__)


class Point(NamedMutableSequence):
    __slots__ = ("x", "y")


@dataclass
class Ball:
    ind: int
    pos: Point


# -- Generate arrow polygons --


def rotated_arrow(points, pos, alpha):
    new_points = []

    cx, cy = pos
    for point in points:
        m = (point[1] - cy) / (point[0] - cx)

        rad = dist(point, (cx, cy))

        angle = atan(m)

        if angle == 0:
            angle = radians(180)

        nx = cos(angle + radians(alpha)) * rad + cx
        ny = sin(angle + radians(alpha)) * rad + cy

        new_points.append((nx, ny))

    return new_points


def get_arrow(cx, cy, size):
    s = size / 2

    points = []

    h = (cx - s, cy)
    r = (cx + s / 2, cy - s)
    re = (cx + s, cy - s / 1.5)
    c = (cx + s / 6, cy)
    le = (cx + s, cy + s / 1.5)
    l = (cx + s / 2, cy + s)

    points.append(h)
    points.append(r)
    points.append(re)
    points.append(c)
    points.append(le)
    points.append(l)

    return points


@dataclass
class Arrow:
    ind: int
    size: int
    _pos: Point
    angle: float = 180

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self):
        self.polygon = get_arrow(self.pos.x, self.pos.y, self.size)

    def __post_init__(self):
        self.polygon = get_arrow(self.pos.x, self.pos.y, self.size)

    def update(self):
        self.polygon = get_arrow(self.pos.x, self.pos.y, self.size)
        self.polygon = rotated_arrow(self.polygon, self.pos, self.angle)

    def rotate(self, angle):
        self.angle = angle
        self.polygon = rotated_arrow(self.polygon, self.pos, self.angle)
