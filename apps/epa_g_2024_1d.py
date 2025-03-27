import marimo

__generated_with = "0.11.29"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import pyarrow
    import numpy as np
    import pandas as pd
    import altair as alt
    return alt, np, pd, pyarrow


@app.cell
def _(mo):
    data_path = (
        mo.notebook_location() / "public"
    )

    ref = data_path.joinpath("referencia.pkl")
    epa_g_1d = data_path.joinpath("epa_galicia_2024_1d.feather")
    return data_path, epa_g_1d, ref


@app.cell
def _(epa_g_1d, pd):
    epa_1d = pd.read_feather(epa_g_1d)
    return (epa_1d,)


@app.cell
def _(epa_1d, np, pd):
    eo_matrix = (
        pd.DataFrame(
            np.array(
                np.meshgrid(
                    epa_1d.query(
                        'AOI=="03"|AOI=="04"'
                    ).ACT1.unique(),
                    epa_1d.query(
                        'AOI=="03"|AOI=="04"'
                    ).OCUP1.unique(),
                )
            ).T.reshape(-1, 2),
            columns=["ACT1", "OCUP1"],
        )
        .merge(
            epa_1d.query(
                'AOI=="03"|AOI=="04"'
            )
            .groupby(["ACT1", "OCUP1"], observed=True)
            .FACTOREL.sum().div(4).astype(int)
            .reset_index(),
            how="left",
        )  
        .pivot_table(index="ACT1", columns="OCUP1", values="FACTOREL")
    )
    return (eo_matrix,)


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
def _(eo_matrix, mo):
    t1 = mo.ui.table(eo_matrix, selection='single-cell', show_column_summaries=False)
    d1 = mo.ui.dropdown(['Edad','Formación','Situación','Estado_Civil'], value='Edad', label='Variable eje horizontal:  ')
    d2 = mo.ui.dropdown(['Edad','Formación','Situación','Estado_Civil'], value='Formación', label='Variable eje horizontal:  ')
    d3 = mo.ui.dropdown(['Sexo','Contrato','Jornada','Nacimiento'], value='Sexo', label='Variable color:  ')
    d4 = mo.ui.dropdown(['Sexo','Contrato','Jornada','Nacimiento'], value='Sexo', label='Variable color:  ')
    return d1, d2, d3, d4, t1


@app.cell
def _(epa_1d, np, referencia, safe_values_column, safe_values_row, t1):
    source = (epa_1d.groupby(["ACT1", "OCUP1"], observed=True)
                        .get_group((safe_values_row(t1), safe_values_column(t1)))
                        .assign(
                            Edad=lambda x: [
                                referencia.query(
                                    'Variable=="EDAD1"'
                                ).Diccionario.values[0][i]
                                for i in x.EDAD1
                            ],
                            Sexo=lambda x: [
                                referencia.query(
                                    'Variable=="SEXO1"'
                                ).Diccionario.values[0][i]
                                for i in x.SEXO1
                            ],
                            Situación=lambda x: [
                                referencia.query(
                                    'Variable=="SITU"'
                                ).Diccionario.values[0][i]
                                for i in x.SITU
                            ],
                            Contrato=lambda x: [
                                referencia.query(
                                    'Variable=="DUCON1"'
                                ).Diccionario.values[0][i]
                                if i != " "
                                else np.nan
                                for i in x.DUCON1
                            ],
                            Jornada=lambda x: [
                                referencia.query(
                                    'Variable=="PARCO1"'
                                ).Diccionario.values[0][int(i)]
                                if i != " "
                                else np.nan
                                for i in x.PARCO1
                            ],
                            Formación=lambda x: [
                                {
                                    "AN": "Analfabetos",
                                    "P1": "Primaria incompleta",
                                    "P2": "Primaria",
                                    "S1": "ESO",
                                    "SG": "Bachiller",
                                    "SP": "FP",
                                    "SU": "Superior",
                                }[i]
                                for i in x.NFORMA
                            ],
                            Estado_Civil=lambda x: [
                                referencia.query(
                                    'Variable=="ECIV1"'
                                ).Diccionario.values[0][i]
                                for i in x.ECIV1
                            ],
                            Nacimiento=lambda x:np.where(x.REGNA1=='   ','España','Extranjero')
                        )
             )
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
