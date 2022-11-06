import pandas as pd
import constants as c
import matplotlib.pyplot as plt

from matplotlib import ticker

FONT_SIZE = 20
FONT_SIZE_TITLE = 25


# This function was copied from the net and adjusted.
@ticker.FuncFormatter
def _major_formatter(x: float | int, pos):
    """
    Format labels in a given plot to a format where
    each 3 digits are separated by underscore.

    :param x: Label to be formatted.
    :param pos: N/A

    :return: str
    """
    return f'{int(x):_}'


def _plot(prefix: str,
          property_types: list | tuple,
          plot_title_type: str,
          plot_title_city: list | tuple | str):
    """
    Put all cleaned and aggregated data into visual form. This is the result of this project.

    :param prefix: Shortcut of a given area.
    :param property_types: Subtypes of flat/house/land.
    :param plot_title_type: name of plot 1
    :param plot_title_city: name of plot 2

    :return: None
    """

    plot_title_type = plot_title_type.upper()
    data = pd.read_csv("result/prices_all_months.csv")
    plt.style.use("dark_background")

    nr_types = len(property_types)
    is_odd = True if nr_types % 2 != 0 else False

    # Add +1 if odd number, to get even number of graphs at a main plot.
    nr_types = nr_types + 1 if is_odd else nr_types

    x, y = int(nr_types / 2), 2
    fig, axes = plt.subplots(x, y, figsize=(19.2, 10.8))
    x_ticks_ = None
    for i, type_ in enumerate(property_types):
        row = i
        column = 0

        # Start new column if the first one is already at the bottom of main plot.
        if row >= x:
            row -= x
            column = 1

        ax = axes[row, column]

        ax.plot(data[c.PERIOD], data[f"{prefix} {type_}"], "o-", c="red")

        if not i:
            x_ticks_ = ax.get_xticks()

        # Add text to each graph.
        ax.text(0.05, 0.80, type_, transform=ax.transAxes,
                bbox=dict(facecolor="yellow", edgecolor="black"), color="black")

        # Format labels at y axis.
        ax.yaxis.set_major_formatter(_major_formatter)

        # Hide ticks on the x axis besides the bottom. Applies for bottom subplots
        #   when number of subplots in even.
        if row < x - 1:
            ax.set_xticks("", visible=False)

        # Make sure that the x ticks are visible also for column that will end
        #   with uneven number of subplots.
        if i == len(property_types) - 1:
            ax.set_xticks(x_ticks_)

        # Delete a subplot when it is empty.
        if is_odd and column and i == len(property_types) - 1:
            fig.delaxes(axes[-1][-1])

    # Add some description of whole plot and of each axis.
    fig.text(0.5, 0.94, f"{plot_title_type}", ha="center", fontsize=FONT_SIZE_TITLE)
    fig.text(0.5, 0.90, f"{plot_title_city}", ha="center", fontsize=FONT_SIZE)
    fig.text(0.06, 0.45, r"$\frac{Cena}{m^{2}}$ [CZK]", ha="center", fontsize=FONT_SIZE, rotation=90)
    fig.text(0.5, 0.02, "Čas [Měsíce]", ha="center", fontsize=FONT_SIZE)

    # Save
    plt.savefig(f"result/{prefix} {plot_title_type}.png")


def plot_all():
    """
    Iterate through locations and types of properties to get plots for each type.

    :return: None
    """
    for prefix, title in zip([c.SHORT_PRAGUE, c.SHORT_TOP9, c.SHORT_REST],
                             [c.TOWNS_PRAGUE[0].title(), c.TOWNS_TOP9_T, c.TOWNS_REST_T]):
        _plot(prefix=prefix,
              property_types=c.TYPES_FLAT,
              plot_title_type=c.FLAT,
              plot_title_city=title)
        _plot(prefix=prefix,
              property_types=c.TYPES_HOUSE,
              plot_title_type=c.HOUSE,
              plot_title_city=title)
        _plot(prefix=prefix,
              property_types=c.TYPES_LAND,
              plot_title_type=c.LAND,
              plot_title_city=title)
