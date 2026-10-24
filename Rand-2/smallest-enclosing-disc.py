import random
import math
import csv
import time
import statistics
import matplotlib.pyplot as plt


class Points:
    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    def x(self):
        return self.__x

    def y(self):
        return self.__y


class Circle:
    def __init__(self, m_x, m_y, r):
        self.__m_x = m_x
        self.__m_y = m_y
        self.__r = r

    def m_x(self):
        return self.__m_x

    def m_y(self):
        return self.__m_y

    def r(self):
        return self.__r


class Disc:
    def __init__(self, points, circle):
        self.__points = points
        self.__circle = circle

    def circle(self):
        return self.__circle

    def points(self):
        return self.__points


def make_circle(p1, p2, p3=None):
    if p3 is None:
        mx = (p1.x() + p2.x()) / 2
        my = (p1.y() + p2.y()) / 2
        r = math.hypot(p1.x() - p2.x(), p1.y() - p2.y()) / 2
        return Circle(mx, my, r)

    bx, by = p2.x() - p1.x(), p2.y() - p1.y()
    cx, cy = p3.x() - p1.x(), p3.y() - p1.y()
    b2 = bx * bx + by * by
    c2 = cx * cx + cy * cy
    det = bx * cy - by * cx

    scale = max(abs(bx * cy), abs(by * cx), 1e-300)

    if abs(det) <= 1e-12 * scale:
        return None

    # de tweede term komt door norm(m) = norm(m-b)= norm(m-c) en dan
    # het oplossen voor m
    mx = p1.x() + (b2 * cy - c2 * by) / (2 * det)
    my = p1.y() + (bx * c2 - cx * b2) / (2 * det)
    r = math.hypot(mx - p1.x(), my - p1.y())
    return Circle(mx, my, r)


def in_circle(p1, circle):
    p_x = p1.x()
    p_y = p1.y()
    m_x = circle.m_x()
    m_y = circle.m_y()
    r = circle.r()
    distance_squared = (p_x - m_x) ** 2 + (p_y - m_y) ** 2
    radius_squared = r**2
    tolerance = 1e-12 * max(distance_squared, radius_squared, 1e-300)
    return distance_squared <= radius_squared + tolerance


def mini_disc(points, rng=None):
    points = list(points)
    n = len(points)

    if n == 0:
        raise ValueError("At least one point is required.")

    if n == 1:
        p = points[0]
        circle = Circle(p.x(), p.y(), 0.0)
        return Disc([p], circle)

    if rng is None:
        rng = random.Random()

    rng.shuffle(points)

    result = Disc(points[:2], make_circle(points[0], points[1]))

    for i in range(2, n):
        if not in_circle(points[i], result.circle()):
            result = Mini_disc_with_point(points[:i], points[i], rng=rng)

    return result


def Mini_disc_with_point(Points, q, rng=None):
    points = list(Points)
    if rng is None:
        rng = random.Random()
    rng.shuffle(points)

    circle = Circle(q.x(), q.y(), 0.0)
    support_points = [q]

    for j, p in enumerate(points):
        if not in_circle(p, circle):
            result = Mini_disc_with_2_points(points[:j], p, q, rng=rng)
            circle = result.circle()
            support_points = result.points()

    return Disc(support_points, circle)


def Mini_disc_with_2_points(Points, q1, q2, rng=None):
    points = list(Points)

    if q1.x() == q2.x() and q1.y() == q2.y():
        return Mini_disc_with_point(points, q1, rng=rng)

    circle = make_circle(q1, q2)
    support_points = [q1, q2]

    for p in points:
        if not in_circle(p, circle):
            circle = make_circle(q1, q2, p)
            if circle is None:
                raise ValueError(
                    "No circle can have q1, q2, and this point on its boundary"
                )

            support_points = [q1, q2, p]

    return Disc(support_points, circle)


def main():

    sizes = [50, 100, 250, 500, 1000, 2000, 4000]

    repetitions = 10

    rng_points = random.Random(12345)
    rng_order = random.Random(54321)

    results = []

    for n in sizes:
        execution_times = []

        for _ in range(repetitions):

            points = [
                Points(rng_points.uniform(0, 1000), rng_points.uniform(0, 1000))
                for _ in range(n)
            ]

            start = time.perf_counter()
            disc = mini_disc(points, rng=rng_order)
            elapsed = time.perf_counter() - start

            if not all(in_circle(p, disc.circle()) for p in points):
                raise RuntimeError(f"The disc does not enclose all points for n={n}.")

            execution_times.append(elapsed)

        average_time = statistics.mean(execution_times)
        best_time = min(execution_times)
        worst_time = max(execution_times)

        results.append(
            {
                "n": n,
                "best_case_complexiteit": "O(n)",
                "worst_case_complexiteit": "O(n^3)",
                "theoritische_gemiddelde_tijd_complexiteit": "Verwacht O(n)",
                "geobserveerde_best_case_tijd_seconden": best_time,
                "geobserveerde_worst_case_tijd_seconden": worst_time,
                "geobserveerde_gemiddelde_tijd_seconden": average_time,
            }
        )

        print(
            f"n={n:5d} | "
            f"beste={best_time:.6f}s | "
            f"gemiddelde={average_time:.6f}s | "
            f"slechtste={worst_time:.6f}s"
        )

    n0 = results[0]["n"]
    average_time0 = results[0]["geobserveerde_gemiddelde_tijd_seconden"]
    worst_time0 = results[0]["geobserveerde_worst_case_tijd_seconden"]

    for row in results:
        size_ratio = row["n"] / n0
        row["relatieve_invoergrootte_n_over_n0"] = size_ratio
        row["geobserveerde_gemiddelde_groeiverhouding"] = (
            row["geobserveerde_gemiddelde_tijd_seconden"] / average_time0
        )
        row["geobserveerde_slechtste_groeiverhouding"] = (
            row["geobserveerde_worst_case_tijd_seconden"] / worst_time0
        )
        row["lineaire_groeireferentie"] = size_ratio
        row["kubische_groeireferentie"] = size_ratio**3

    csv_filename = "smallest_enclosing_disc_results.csv"

    fieldnames = [
        "n",
        "best_case_complexiteit",
        "worst_case_complexiteit",
        "theoritische_gemiddelde_tijd_complexiteit",
        "geobserveerde_best_case_tijd_seconden",
        "geobserveerde_worst_case_tijd_seconden",
        "geobserveerde_gemiddelde_tijd_seconden",
        "relatieve_invoergrootte_n_over_n0",
        "geobserveerde_gemiddelde_groeiverhouding",
        "geobserveerde_slechtste_groeiverhouding",
        "lineaire_groeireferentie",
        "kubische_groeireferentie",
    ]

    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        writer.writerows(results)

    plt.figure(figsize=(9, 6))

    relative_sizes = [row["relatieve_invoergrootte_n_over_n0"] for row in results]

    plt.loglog(
        relative_sizes,
        [row["geobserveerde_gemiddelde_groeiverhouding"] for row in results],
        marker="o",
        label="Geobserveerde gemiddelde groei",
    )
    plt.loglog(
        relative_sizes,
        [row["geobserveerde_slechtste_groeiverhouding"] for row in results],
        marker="s",
        label="Slechtste gemeten groei (10 herhalingen)",
    )
    plt.loglog(
        relative_sizes,
        [row["lineaire_groeireferentie"] for row in results],
        linestyle="--",
        label="Lineaire groeireferentie O(n)",
    )
    plt.loglog(
        relative_sizes,
        [row["kubische_groeireferentie"] for row in results],
        linestyle=":",
        label="Kubische groeireferentie O(n³)",
    )

    plt.xlabel("Relatieve invoergrootte (n / n₀)")
    plt.ylabel("Relatieve groeitijd (T(n) / T(n₀))")
    plt.title("Genormaliseerde groei van de kleinste insluitende schijf")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    png_filename = "smallest_enclosing_disc_growth.png"
    plt.savefig(png_filename, dpi=300, bbox_inches="tight")
    plt.show()

    print(f"\nGrafiek opgeslagen als: {png_filename}")
    print(f"Resultaten opgeslagen als: {csv_filename}")


if __name__ == "__main__":
    main()
