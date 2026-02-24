"""
Вариант 3-3:
Левая функция f(x) = math.sin(x);
Правая функция g(x) = 1 / (x-7).
"""

from math import sin as sin
from visualization import visualize


def f(x: float):
    return sin(x)


def g(x: float):
    return 1 / (x - 7)


def calculate_result(x, n):
    """
    Примеры:
    >>> g(7)
    Traceback (most recent call last):
    ...
    ZeroDivisionError: division by zero

    >>> calculate_result(0, 5)  # x < n, sin(0) = 0.0
    0.0

    >>> calculate_result(8, 5)  # x >= n, g(8) = 1/(8-7) = 1.0
    1.0

    >>> calculate_result(5, 5)  # x == n -> правая ветка
    -0.5

    >>> calculate_result(7, 10)  # 7 < 10 -> sin(7)
    0.6569865987187891

    >>> calculate_result(7, 5)   # 7 >= 5 -> g(7) = None
    ...

    >>> calculate_result(7, 7)   # 7 >= 7 -> g(7) = None
    ...

    >>> calculate_result('a', 5)  # некорректный x -> TypeError
    Traceback (most recent call last):
        ...
    TypeError: '<' not supported between instances of 'str' and 'int'

    >>> calculate_result(5, 'b')  # некорректный n -> TypeError
    Traceback (most recent call last):
        ...
    TypeError: '<' not supported between instances of 'int' and 'str'

    Проверка нескольких значений (цикл):
    >>> for x in (0, 2, 8, 7):
    ...     print(calculate_result(x, 5))
    0.0
    0.9092974268256817
    1.0
    None
    """

    return f(x) if x < n else g(x)


def main():
    try:
        print("Введите n1:")
        n1 = float(input())
        print("Введите n2:")
        n2 = float(input())

    except:
        raise ValueError("X или N должны быть float")

    rx = [i for i in range(-100, 100)]

    # Первый график для n1
    visualize(f, g, n1, rx, title=f'График для n = {n1}')

    # Второй график для n2
    visualize(f, g, n2, rx, title=f'График для n = {n2}')


if __name__ == '__main__':
    main()
