import pandas as pd
import constants as c
import matplotlib.pyplot as plt

from matplotlib import ticker

FONT_SIZE = 20
FONT_SIZE_TITLE = 25


# this function I had to copy from the net... and adjust
@ticker.FuncFormatter
def major_formatter(x, pos):
    return f'{int(x):_}'


def plot_(prefix,
          property_types,
          plot_title_type,
          plot_title_city):
    plot_title_type = plot_title_type.upper()
    plt.style.use("dark_background")
    data = pd.read_csv("result/prices_all_months.csv")
    nr_types = len(property_types)
    nr_types = nr_types + 1 if nr_types % 2 != 0 else nr_types
    x, y = int(nr_types / 2), 2
    fig, axes = plt.subplots(x, y, figsize=(16, 9))

    for i, type_ in enumerate(property_types):
        row = i
        column = 0
        if row >= x:
            row -= x
            column = 1
        ax = axes[row, column]
        ax.plot(data[c.PERIOD], data[f"{prefix} {type_}"], "o-", c="red")
        ax.text(0.05, 0.80, type_, transform=ax.transAxes,
                bbox=dict(facecolor="yellow", edgecolor="black"), color="black")
        ax.yaxis.set_major_formatter(major_formatter)
        if row < x - 1:
            ax.set_xticks("", visible=False)

    fig.text(0.5, 0.94, f"{plot_title_type}", ha="center", fontsize=FONT_SIZE_TITLE)
    fig.text(0.5, 0.90, f"{plot_title_city}", ha="center", fontsize=FONT_SIZE)
    fig.text(0.06, 0.45, r"$\frac{Cena}{m^{2}}$ [CZK]", ha="center", fontsize=FONT_SIZE, rotation=90)
    fig.text(0.5, 0.02, "Období [Měsíce]", ha="center", fontsize=FONT_SIZE)

    # todo: save fig

    plt.show()


skips = (len(c.TYPES_FLAT), len(c.TYPES_HOUSE), len(c.TYPES_LAND))
print(skips)


def plot_all():
    for prefix, title in zip([c.SHORT_PRAGUE, c.SHORT_TOP9, c.SHORT_REST],
                             [c.TOWNS_PRAGUE, c.TOWNS_TOP9, c.TOWNS_REST_TITLE]):
        plot_(prefix=prefix,
              property_types=c.TYPES_FLAT,
              plot_title_type=c.FLAT,
              plot_title_city=title)
        # plot_(prefix=prefix,
        #       property_types=c.TYPES_HOUSE,
        #       plot_title_type=c.HOUSE,
        #       plot_title_city=title)
        # plot_(prefix=prefix,
        #       property_types=c.TYPES_LAND,
        #       plot_title_type=c.LAND,
        #       plot_title_city=title)


plot_all()
