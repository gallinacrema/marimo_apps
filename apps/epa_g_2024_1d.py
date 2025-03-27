import marimo

__generated_with = "0.11.28"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import pandas as pd
    import altair as alt
    return alt, pd


@app.cell
def _(mo):
    data_path = (
        mo.notebook_location() / "public"
    )

    eo = data_path.joinpath("eo_matrix.feather")
    ref = data_path.joinpath("referencia.pkl")
    src = data_path.joinpath("source.feather")
    return data_path, eo, ref, src


@app.cell
def safe_values_row():
    def safe_values_row(table):
        try:
            return table.value[0].row
        except IndexError:
            return '1'
    return (safe_values_row,)


@app.cell
def safe_values_column():
    def safe_values_column(table):
        try:
            return table.value[0].column
        except IndexError:
            return '1'
    return (safe_values_column,)


@app.cell
def _(pd, ref):
    referencia = pd.read_pickle(ref, compression=None)
    return (referencia,)


@app.cell
def _(referencia):
    x_labels = {'Edad': list(referencia.query('Variable=="EDAD1"').Diccionario.values[0].values()),
                'Formación': ["Analfabetos", "Primaria incompleta", "Primaria", "ESO", "Bachiller", "FP", "Superior"],
                'Situación': list(referencia.query('Variable=="SITU"').Diccionario.values[0].values()),
                'Estado_Civil': list(referencia.query('Variable=="ECIV1"').Diccionario.values[0].values())
               }
    return (x_labels,)


@app.cell
def _(eo, pd):
    eo_matrix = pd.read_feather(eo)
    return (eo_matrix,)


@app.cell
def _(eo_matrix, mo):
    t1 = mo.ui.table(eo_matrix, selection='single-cell', show_column_summaries=False)
    d1 = mo.ui.dropdown(['Edad','Formación','Situación','Estado_Civil'], value='Edad', label='Variable eje horizontal:  ')
    d2 = mo.ui.dropdown(['Edad','Formación','Situación','Estado_Civil'], value='Formación', label='Variable eje horizontal:  ')
    d3 = mo.ui.dropdown(['Sexo','Contrato','Jornada','Nacimiento'], value='Sexo', label='Variable color:  ')
    d4 = mo.ui.dropdown(['Sexo','Contrato','Jornada','Nacimiento'], value='Sexo', label='Variable color:  ')
    return d1, d2, d3, d4, t1


@app.cell
def _(pd, src):
    source = pd.read_feather(src)
    return (source,)


@app.cell
def _(
    alt,
    d1,
    d2,
    d3,
    d4,
    mo,
    referencia,
    safe_values_column,
    safe_values_row,
    source,
    t1,
    x_labels,
):
    mo.vstack(
        (
            mo.md(
                referencia.query('Variable=="ACT1"').Diccionario.values[0][
                    safe_values_row(t1) if safe_values_row(t1) != "0" else 0
                ]
                + "<br>"
                + referencia.query('Variable=="OCUP1"').Diccionario.values[0][
                    safe_values_column(t1) if safe_values_column(t1) != "0" else 0
                ]
            ),
            t1,
            mo.hstack(
                (
                    mo.vstack((d1,d3,
                    alt.Chart(source.groupby([d1.value, d3.value])
                        .FACTOREL.sum()
                        .div(4)
                        .reset_index()
                    )
                    .mark_bar()
                    .encode(
                        alt.X(d1.value+":N").scale(domain=x_labels[d1.value]).axis(title=None, labelAngle=45),
                        alt.Y("FACTOREL:Q").axis(title=None),
                        alt.Color(d3.value).legend(title=None),
                    )
                    .properties(height=200, width=300))),
                     mo.vstack((d2,d4,
                    alt.Chart(source.groupby([d2.value, d4.value])
                        .FACTOREL.sum()
                        .div(4)
                        .reset_index()
                    )
                    .mark_bar()
                    .encode(
                        alt.X(d2.value+":N").scale(domain=x_labels[d2.value]).axis(title=None, labelAngle=45),
                        alt.Y("FACTOREL:Q").axis(title=None),
                        alt.Color(d4.value).legend(title=None),
                    )
                    .properties(height=200, width=300)),
                ),
            ),
        )
    )
    )
    return


if __name__ == "__main__":
    app.run()
