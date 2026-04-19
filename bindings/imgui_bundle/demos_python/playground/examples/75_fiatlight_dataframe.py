"""# Fiatlight: Titanic DataFrame Explorer

[Fiatlight](https://pthom.github.io/fiatlight) turns Python functions into interactive apps with visual pipelines.

This demo shows a **filterable dataframe** with linked plots:
- Filter the Titanic dataset by class, survival, sex, age
- See a survival rate pie chart and age histogram update in real time

The dataframe is loaded from the web (Data Science Dojo repository).

**Links:**
- [Fiatlight documentation](https://pthom.github.io/fiatlight)
- [Fiatlight repository](https://github.com/pthom/fiatlight)
"""
import fiatlight as fl
import pandas as pd
from enum import Enum
from imgui_bundle import implot, hello_imgui
import numpy as np


# ============================================================
#  Part 1 - Standard Python functions
#  (these functions don't know about Fiatlight)
# ============================================================

def make_titanic_dataframe() -> pd.DataFrame:
    """Download the Titanic dataset from the web.
    Uses immapp.download_url_bytes which works on both desktop and Pyodide
    (pandas' read_csv(url) fails on Pyodide because urllib has no socket layer).
    """
    import io
    from imgui_bundle import immapp
    url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
    csv_bytes = immapp.download_url_bytes(url)
    if len(csv_bytes) > 0:
        return pd.read_csv(io.BytesIO(csv_bytes))
    print("Error: failed to download Titanic dataset")
    return pd.DataFrame()


# Load once at startup
TITANIC_DATAFRAME = make_titanic_dataframe()


class Sex(Enum):
    Man = "male"
    Woman = "female"


def show_filterable_dataframe(
    passenger_class: int | None = None,
    survived: bool | None = None,
    sex: Sex | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
) -> pd.DataFrame:
    """Filter the Titanic dataset by various criteria."""
    df = TITANIC_DATAFRAME
    if df.empty:
        return df
    if survived is not None:
        df = df[df["Survived"] == int(survived)]
    if passenger_class is not None:
        df = df[df["Pclass"] == passenger_class]
    if sex:
        df = df[df["Sex"] == sex.value]
    if age_min is not None:
        df = df[df["Age"] >= age_min]
    if age_max is not None:
        df = df[df["Age"] <= age_max]
    return df


def survival_rate_plot(df: pd.DataFrame) -> None:
    """Pie chart showing survival rate."""
    total = df["Survived"].count()
    if total == 0:
        return
    survived = df["Survived"].sum()
    dead = total - survived
    percents = np.array(
        [survived / total * 100, dead / total * 100])
    labels = ["Survived", "Died"]
    plot_size = hello_imgui.em_to_vec2(20, 20)
    if implot.begin_plot("Survival Rate", size=plot_size):
        implot.plot_pie_chart(
            label_ids=labels, values=percents,
            x=0.5, y=0.5, radius=0.4, label_fmt="%.1f%%")
        implot.end_plot()

def age_histogram_plot(df: pd.DataFrame) -> None:
    """Histogram of passenger ages."""
    if df.empty or "Age" not in df.columns:
        return
    plot_size = hello_imgui.em_to_vec2(30, 20)
    if implot.begin_plot("Age Distribution", size=plot_size):
        implot.setup_axes(
            x_label="Age", y_label="Count",
            x_flags=implot.AxisFlags_.auto_fit,
            y_flags=implot.AxisFlags_.auto_fit)
        ages = df["Age"].dropna().values
        implot.plot_histogram(
            "Age", ages, bins=30)  # type: ignore
        implot.end_plot()


# ============================================================
#  Part 2 - Define a GUI with Fiatlight
# ============================================================

# Add attributes to the filter function
# (ranges, labels, widget sizes for the output)
fl.add_fiat_attributes(
    show_filterable_dataframe,
    label="Titanic Data",
    age_min__range=(0, 100),
    age_max__range=(0, 100),
    passenger_class__range=(1, 3),
    passenger_class__label="Passenger Class",
    # return__widget_size_em=(55.0, 15.0),
    # return__rows_per_page_node=15,
    # return__column_widths_em={"Name": 5},
)


def main() -> None:
    graph = fl.FunctionsGraph()
    graph.add_function(show_filterable_dataframe)
    # Link the filter output to both plots
    graph.add_gui_node(age_histogram_plot)
    graph.add_link(
        show_filterable_dataframe, age_histogram_plot)
    graph.add_gui_node(survival_rate_plot)
    graph.add_link(
        show_filterable_dataframe, survival_rate_plot)
    fl.run(graph,
           app_name="dataframe_with_gui_demo_titanic")


if __name__ == "__main__":
    main()
