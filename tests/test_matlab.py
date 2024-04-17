import mat2py as mp
from mat2py.core import *


def main():
    n = M[0:15]
    x = 0.84**n
    y = circshift(x, 5)
    c, lags = xcorr(x, y, 10, "normalized")
    stem(lags, c)


if __name__ == "__main__":
    main()