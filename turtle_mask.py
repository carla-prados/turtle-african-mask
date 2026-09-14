#!/usr/bin/env python3
"""Redraw turtle-afrincan-mask.sb without Small Basic.

A faithful-enough Small Basic Turtle: GraphicsWindow's Y axis points DOWN,
angle 0 points UP, and positive turns go clockwise. Turtle.MoveTo turns the
turtle to face its target before moving, which matters here because the
original repeatedly resets its heading with Turn(-Turtle.Angle).

    python turtle_mask.py                # mask.png at the original sides = 50
    python turtle_mask.py --sides 6      # the same drawing, coarser
    python turtle_mask.py --grid         # 3 / 6 / 12 / 50 side by side
"""
import argparse
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class Turtle:
    def __init__(self, x=0.0, y=0.0):
        self.x, self.y, self.angle = x, y, 0.0
        self.pen = True
        self.width, self.color = 3, "Olive"
        self.segments = []

    def _dir(self):
        t = math.radians(self.angle)
        return math.sin(t), -math.cos(t)

    def turn(self, a):    self.angle = (self.angle + a) % 360
    def turn_right(self): self.turn(90)
    def turn_left(self):  self.turn(-90)
    def pen_up(self):     self.pen = False
    def pen_down(self):   self.pen = True

    def move(self, d):
        dx, dy = self._dir()
        nx, ny = self.x + dx * d, self.y + dy * d
        if self.pen:
            self.segments.append((self.x, self.y, nx, ny, self.width, self.color))
        self.x, self.y = nx, ny

    def move_to(self, x, y):
        dx, dy = x - self.x, y - self.y
        if dx or dy:
            self.angle = math.degrees(math.atan2(dx, -dy)) % 360
        if self.pen:
            self.segments.append((self.x, self.y, x, y, self.width, self.color))
        self.x, self.y = x, y


def draw_mask(sides=50):
    """Transcription of the 2018 program, line for line."""
    t = Turtle(300, 400)

    def arc(total_length, total_turn):
        # The whole drawing rests on this: an arc as `sides` short straight
        # moves. Dividing BOTH quantities by `sides` keeps the arc identical
        # as the resolution changes.
        length, angle = total_length / sides, total_turn / sides
        for _ in range(sides):
            t.move(length)
            t.turn(angle)

    # Face: two 90-degree arcs meeting at a point
    t.turn(-45); arc(400, 90)
    t.turn(90);  arc(400, 90)

    # Eyes: four circles. Only the first resets its heading; the other three
    # turn right from wherever MoveTo left them. Kept exactly as written.
    t.pen_up(); t.move_to(250, 150); t.pen_down(); t.turn(-t.angle); arc(60, 360)
    t.pen_up(); t.move_to(350, 150); t.pen_down(); t.turn_right();   arc(60, 360)
    t.pen_up(); t.move_to(240, 150); t.pen_down(); t.turn_right();   arc(100, 360)
    t.pen_up(); t.move_to(360, 150); t.pen_down(); t.turn_right();   arc(100, 360)

    # Mouth
    t.width, t.color = 7, "Brown"
    t.pen_up(); t.move_to(280, 300); t.pen_down()
    t.turn(-t.angle); t.turn_right(); t.move(50)

    # Nose: two strokes from a shared apex
    t.width, t.color = 3, "Olive"
    t.pen_up(); t.move_to(300, 200); t.pen_down()
    for side in (t.turn_left, t.turn_right):
        t.turn(-t.angle); t.turn(180); t.move(40); side(); t.move(20)
        t.move_to(300, 200)

    # Chin
    t.pen_up(); t.move_to(300, 425); t.pen_down()
    t.turn(-t.angle)
    t.turn(-45); arc(450, 90)
    t.turn(90);  arc(450, 90)
    return t.segments


COLOURS = {"Olive": "#6b8e23", "Brown": "#8b4513"}
BACKGROUND = "#fffacd"          # LemonChiffon, as in the original


def plot(ax, sides, title=""):
    for x1, y1, x2, y2, w, c in draw_mask(sides):
        ax.plot([x1, x2], [y1, y2], color=COLOURS[c], lw=w * 0.6,
                solid_capstyle="round")
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.axis("off")
    ax.set_facecolor(BACKGROUND)
    if title:
        ax.set_title(title, fontsize=11)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sides", type=int, default=50,
                    help="segments per arc: the resolution knob (default 50)")
    ap.add_argument("--grid", action="store_true",
                    help="draw 3 / 6 / 12 / 50 side by side")
    ap.add_argument("-o", "--out", default="mask.png")
    args = ap.parse_args()

    if args.grid:
        fig, axes = plt.subplots(1, 4, figsize=(13, 4.5), facecolor=BACKGROUND)
        for ax, s in zip(axes, (3, 6, 12, 50)):
            plot(ax, s, f"sides = {s}")
    else:
        fig, ax = plt.subplots(figsize=(5, 6), facecolor=BACKGROUND)
        plot(ax, args.sides)

    fig.savefig(args.out, dpi=140, bbox_inches="tight", facecolor=BACKGROUND)
    print(f"wrote {args.out}  (sides = {args.sides})")


if __name__ == "__main__":
    main()
