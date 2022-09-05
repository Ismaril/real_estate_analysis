import pandas as pd
import constants as c
import matplotlib.pyplot as plt

from matplotlib import ticker

FONT_SIZE = 20
FONT_SIZE_TITLE = 25


# this function I had to copy from the net... and adjust
@ticker.FuncFormatter
def major_formatter(x: float | int, pos):
    """
    Format labels in a given plot to a format where
    each 3 digits are separated by underscore

    :param x: Label to be formatted
    :param pos: N/A
    :return: str
    """
    return f'{int(x):_}'


def plot_(prefix: str,
          property_types: list | tuple,
          plot_title_type: str,
          plot_title_city: list | tuple | str):
    """
    Put all cleaned and aggregated data into visual form. This is the result of this project.

    :param prefix: Shortcut of a given area
    :param property_types: subtypes of flat/house/land
    :param plot_title_type: name of plot 1
    :param plot_title_city: name of plot 2
    :return: matplotlib.pyplot.plot
    """

    plot_title_type = plot_title_type.upper()
    data = pd.read_csv("result/prices_all_months.csv")
    plt.style.use("dark_background")

    nr_types = len(property_types)

    # add +1 if odd number, to get even number of graphs at a main plot
    nr_types = nr_types + 1 if nr_types % 2 != 0 else nr_types

    x, y = int(nr_types / 2), 2
    fig, axes = plt.subplots(x, y, figsize=(16, 9))

    for i, type_ in enumerate(property_types):
        row = i
        column = 0

        if row >= x:  # start new column if the first one is already at the bottom of main plot
            row -= x
            column = 1

        ax = axes[row, column]

        ax.plot(data[c.PERIOD], data[f"{prefix} {type_}"], "o-", c="red")

        # add text to each graph
        ax.text(0.05, 0.80, type_, transform=ax.transAxes,
                bbox=dict(facecolor="yellow", edgecolor="black"), color="black")

        # format labels at y axis
        ax.yaxis.set_major_formatter(major_formatter)

        # hide ticks on the x axis besides the bottom
        if row < x - 1:
            ax.set_xticks("", visible=False)

    # add some description of whole plot and of each axis
    fig.text(0.5, 0.94, f"{plot_title_type}", ha="center", fontsize=FONT_SIZE_TITLE)
    fig.text(0.5, 0.90, f"{plot_title_city}", ha="center", fontsize=FONT_SIZE)
    fig.text(0.06, 0.45, r"$\frac{Cena}{m^{2}}$ [CZK]", ha="center", fontsize=FONT_SIZE, rotation=90)
    fig.text(0.5, 0.02, "Období [Měsíce]", ha="center", fontsize=FONT_SIZE)

    # save as png img
    plt.savefig(f"result/{prefix} {plot_title_type}.png")


def plot_all():
    """
    Iterate through locations and types of properties to get plots for each type

    :return: None
    """
    for prefix, title in zip([c.SHORT_PRAGUE, c.SHORT_TOP9, c.SHORT_REST],
                             [c.TOWNS_PRAGUE, c.TOWNS_TOP9, c.TOWNS_REST_TITLE]):
        plot_(prefix=prefix,
              property_types=c.TYPES_FLAT,
              plot_title_type=c.FLAT,
              plot_title_city=title)
        plot_(prefix=prefix,
              property_types=c.TYPES_HOUSE,
              plot_title_type=c.HOUSE,
              plot_title_city=title)
        plot_(prefix=prefix,
              property_types=c.TYPES_LAND,
              plot_title_type=c.LAND,
              plot_title_city=title)


plot_all()
