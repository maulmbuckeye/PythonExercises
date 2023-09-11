from turtle import *
from math import acos, pi

speed(0)
tracer(1000)


def KochCurve(length, level):  # noqa
    if level == 0:
        fd(length)
        return

    flat_section = 0.48
    to_peak_section = 0.5 - flat_section
    angle = acos(to_peak_section / flat_section) * 180 / pi

    instuctions = [(0, 1/3), (60, 1/3), (-120, 1/3), (60, 1/3)]

    instuctions = [(0, flat_section), (angle, flat_section), (-2 * angle, flat_section), (angle, flat_section)]
    for turn, percent_of_length in instuctions:
        lt(turn)
        KochCurve(length * percent_of_length, level - 1)


if __name__ == '__main__':
    full_length = 500

    KochCurve(400, 3)
    update()
    input("Hit enter to finish")



