import pandas as pd
import matplotlib.pyplot as plt
import constants as c


def plot_all():
    data = pd.read_csv("result/prices_all_months.csv")
    nr_types = len(c.TYPES_FLAT)
    nr_types = nr_types + 1 if nr_types % 2 != 0 else nr_types
    x, y = int(nr_types/2), 2

    # Flats
    fig, axes = plt.subplots(x, y, figsize=(16, 9))
    columns = data.columns

    ax = axes[0, 0]  # we can acces the first plot (top left) by index zero, because the whole graph is one dimensional

    ax.plot(data[c.PERIOD], data[columns[0]])
    ax.set_title("Trial 1")  # set the title name of the plot
    ax.text(0.05, 0.81, columns[0][4:], transform=ax.transAxes, bbox=dict(facecolor="yellow", edgecolor="black"))
    ax.legend(loc="upper right", fancybox=False, edgecolor="black")  # fancy box is just type of box under the text

    fig.text(0.06, 0.45, r"$\frac{Price}{m^{2}}$ [CZK]", ha="center", fontsize=20)  # add label to more plots together
    fig.text(0.5, 0.02, "Period [Months]", ha="center", fontsize=20)  # add label to more plots together
    plt.show()


plot_all()
