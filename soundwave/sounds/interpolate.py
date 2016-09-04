from __future__ import division
import math


def powers_of(x):
    xn = 1
    while True:
        yield xn
        xn *= x


class PiecewisePolynomialInterpolator(object):
    def __init__(self, *polynomials):
        self.polynomials = polynomials
        self.order = max(len(p) for p in polynomials)

    def __call__(self, data, numerator, denominator=1):
        index, remainder = divmod(numerator, denominator)
        dt = remainder / denominator
        index = int(index)
        output = 0
        for t, (polynomial, input) in enumerate(
            zip(
                self.polynomials,
                data[index:index-len(self.polynomials):-1]
            )
        ):
            for term, xn in zip(polynomial, powers_of(t + dt)):
                output += term * xn
        for t, (polynomial, input) in enumerate(
            zip(
                self.polynomials,
                data[index+1:index+1+len(self.polynomials)]
            )
        ):
            for term, xn in zip(polynomial, powers_of(t + 1 - dt)):
                output += term * xn
        return output


# interpolators largely from http://yehar.com/blog/wp-content/uploads/2009/08/deip.pdf
# (we only implement symmetric  :P)
linear = PiecewisePolynomialInterpolator((1, -1))
bspline4_3 = PiecewisePolynomialInterpolator(
    (2/3, 0, -1, 1/2),
    (4/3, -2, 1, -1/6),
)
bspline6_5 = PiecewisePolynomialInterpolator(
    (11/20, 0, -1/2, 0, 1/4, -1/12),
    (17/40, 5/8, -7/4, 5/4, -3/8, 1/24),
    (81/40, -27/8, 9/4, -3/4, 1/8, -1/120),
)
lagrange4_3 = PiecewisePolynomialInterpolator(
    (1, -1/2, -1, 1/2),
    (1, -11/6, 1, -1/6),
)
lagrange6_5 = PiecewisePolynomialInterpolator(
    (1, -1/3, -5/4, 5/12, 1/4, -1/12),
    (1, -13/12, -5/8, 25/24, -3/8, 1/24),
    (1, -137/60, 15/8, -17/24, 1/8, -1/120),
)
hermite4_3 = PiecewisePolynomialInterpolator(
    (1, 0, -5/2, 3/2),
    (2, -4, 5/2, -1/2),
)
hermite6_3 = PiecewisePolynomialInterpolator(
    (1, 0, -7/3, 4/3),
    (5/2, -59/12, 3, -7/12),
    (-3/2, 7/4, -2/3, 1/12),
)
hermite6_5 = PiecewisePolynomialInterpolator(
    (1, 0, -25/12, 5/12, 13/12, -5/12),
    (1, 5/12, -35/8, 35/8, -13/8, 5/24),
    (3, -29/4, 155/24, -65/24, 13/24, -1/24),
)
watte = PiecewisePolynomialInterpolator(
    (1, -1/2, -1/2),
    (1, -3/2, 1/2),
)
optimal2x2_3 = PiecewisePolynomialInterpolator(
    (0.80607906469176971,
     0.17594740788514596,
     -2.35977550974341630,
     1.57015627178718420
    ),
)
