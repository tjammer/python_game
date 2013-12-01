import math

"""vector functions and general help functions for rectangle
and collision detection"""


def magnitude(x, y):
    return math.sqrt(x**2 + y**2)


def dot_product(x1, y1, x2, y2):
    return (x1 * x2 + y1 * y2)


def min_max(points, axis):
    mx = max(dot_product(point[0], point[1], axis[0],
                         axis[1]) for point in points)
    mn = min(dot_product(point[0], point[1], axis[0],
                         axis[1]) for point in points)
    return mn, mx


def overlap(a_min, a_max, b_min, b_max):
    if not (a_max < b_min or b_max < a_min):
        return True, min(a_max - b_min, b_max - a_min)
    else:
        return False, 0


def collides(rect1, rect2):

    # s_points are own points, r_points for other rect2
    s_points = [[rect1.x1, rect1.y1], [rect1.x2, rect1.y2],
                [rect1.x3, rect1.y3], [rect1.x4, rect1.y4]]
    r_points = [[rect2.x1, rect2.y1], [rect2.x2, rect2.y2],
                [rect2.x3, rect2.y3], [rect2.x4, rect2.y4]]

    # four axis
    s_axis1 = [rect1.axis1x, rect1.axis1y]
    s_axis2 = [rect1.axis2x, rect1.axis2y]
    r_axis1 = [rect2.axis1x, rect2.axis1y]
    r_axis2 = [rect2.axis2x, rect2.axis2y]

    # first check
    s_min, s_max = min_max(s_points, s_axis1)
    r_min, r_max = min_max(r_points, s_axis1)
    ovr1 = overlap(s_min, s_max, r_min, r_max) + (s_axis1,)

    if ovr1[0]:
        # second check
        s_min, s_max = min_max(s_points, s_axis2)
        r_min, r_max = min_max(r_points, s_axis2)
        ovr2 = overlap(s_min, s_max, r_min, r_max) + (s_axis2,)
        if ovr2[0]:
            s_min, s_max = min_max(s_points, r_axis1)
            r_min, r_max = min_max(r_points, r_axis1)
            ovr3 = overlap(s_min, s_max, r_min, r_max) + (r_axis1,)
            if ovr3[0]:
                s_min, s_max = min_max(s_points, r_axis2)
                r_min, r_max = min_max(r_points, r_axis2)
                ovr4 = overlap(s_min, s_max, r_min, r_max) + (r_axis2,)
                if ovr4[0]:
                    ovr_list = [ovr1, ovr2, ovr3, ovr4]
                    ovrlap = min(i[1] for i in ovr_list)
                    min_axis = [i[2] for i in ovr_list if ovrlap in i][0]

                    return ovrlap, min_axis
    return False
