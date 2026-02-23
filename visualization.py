from matplotlib import pyplot as plt


def visualize(f, g, n, x_range, title):
    left_x = [x for x in x_range if x < n]
    right_x = [x for x in x_range if x >= n]

    left_y = [f(x) for x in left_x]
    right_y = [g(x) for x in right_x]

    plt.figure()
    plt.title(title)
    plt.plot(left_x, left_y, 'b-', label=f'f(x) = sin(x), x < {n}')
    plt.plot(right_x, right_y, 'r-', label=f'g(x) = 1/(x-7), x ≥ {n}')
    plt.legend()
    plt.grid(True)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.show()
