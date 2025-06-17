import marimo

__generated_with = "0.13.11"
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
    return alt, np, pd


@app.cell
def _(mo):
    data_path = (
        mo.notebook_location() / "public"
    )

    epa_g_2d = data_path.joinpath("ocupados_galicia_2024_2d.feather")
    cnae2009 = data_path.joinpath("cnae2009.feather")
    cno2011 = data_path.joinpath("cno2011.feather")
    cnae =  data_path.joinpath("cnae_2d_to_epa.feather")
    cned =  data_path.joinpath("cned_2d_to_epa.feather")
    referencia_pkl = data_path.joinpath("referencia.pkl")
    matriz =  data_path.joinpath("MIOGAL21_Simetrica.feather")
    nomes_epa = data_path.joinpath("nomes_epa.feather")
    return cnae, cned, cno2011, epa_g_2d, nomes_epa, referencia_pkl


@app.cell
def _():
    age_continuous_to_epa_5y_bins = [0, 4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54, 59, 64, 109]
    return (age_continuous_to_epa_5y_bins,)


@app.cell
def _(cnae, cned, cno2011, nomes_epa, pd, referencia_pkl):
    cnae_2d_to_epa = pd.read_feather(cnae).to_dict()['Nuevo_codigo']
    cned_2d_to_epa = pd.read_feather(cned).to_dict()['Nuevo_codigo']
    cno = pd.read_feather(cno2011).astype('str').apply(lambda x:[i.lstrip('<b>').rstrip('</b>') for i in x])
    nomes = pd.read_feather(nomes_epa).set_index('Código').to_dict()
    referencia = pd.read_pickle(referencia_pkl)
    return cnae_2d_to_epa, cned_2d_to_epa, cno, nomes, referencia


@app.cell
def _(
    age_continuous_to_epa_5y_bins,
    cnae_2d_to_epa,
    cned_2d_to_epa,
    epa_g_2d,
    pd,
    referencia,
):
    epa_2d = pd.read_feather(epa_g_2d).assign(
        EDAD=lambda x: pd.cut(
            x.EDAD1.astype(int),
            bins=age_continuous_to_epa_5y_bins,
            labels=list(
                referencia.query('Variable=="EDAD1"').Diccionario.values[0].keys()
            ),
            include_lowest=True,
        ),
        FORMA=lambda x: x.NFORMA.astype('str').replace(cned_2d_to_epa).astype('category'),
        Sector=lambda x: x.ACT.astype('str').replace(cnae_2d_to_epa).astype('category'),
        Ocupación=lambda x:[i[:-1] if i!=None else i for i in x.OCUP.astype('str')]
    )
    epa_2d.Ocupación = epa_2d.Ocupación.astype('category')
    return (epa_2d,)


@app.cell
def _(epa_2d, np, pd):
    eo_matrix = (
        pd.DataFrame(
            np.array(
                np.meshgrid(
                    epa_2d.Sector.unique(),
                    epa_2d.Ocupación.unique(),
                )
            ).T.reshape(-1, 2),
            columns=["Sector", "Ocupación"],
        )
        .merge(
            epa_2d.groupby(["Sector", "Ocupación"], observed=True)
            .Factor.sum().div(4).astype(int)
            .reset_index(),
            how="left",
        )
        .pivot_table(index="Sector", columns="Ocupación", values="Factor")
    )
    return (eo_matrix,)


@app.function
def safe_values_row(table):
    try:
        return table.value[0].row
    except IndexError:
        return '01'


@app.function
def safe_values_column(table):
    try:
        return table.value[0].column
    except IndexError:
        return '1'


@app.cell
def _(referencia):
    x_labels = {'Idade': list(referencia.query('Variable=="EDAD1"').Diccionario.values[0].values()),
                'Formación': ["Analfabetos", "Primaria incompleta", "Primaria", "ESO", "Bachiller", "FP", "Superior"],
                'Situación': list(referencia.query('Variable=="SITU"').Diccionario.values[0].values()),
                'Estado_Civil': list(referencia.query('Variable=="ECIV1"').Diccionario.values[0].values())
               }
    return (x_labels,)


@app.cell
def _(eo_matrix, mo):
    t1 = mo.ui.table(eo_matrix, selection='single-cell', show_column_summaries=False, pagination=False)
    d1 = mo.ui.dropdown(['Idade','Formación','Situación','Estado_Civil'], value='Idade', label='Variable eixo horizontal:  ')
    d2 = mo.ui.dropdown(['Idade','Formación','Situación','Estado_Civil'], value='Formación', label='Variable eixo horizontal:  ')
    d3 = mo.ui.dropdown(['Sexo','Contrato','Jornada','Nacemento'], value='Sexo', label='Variable color:  ')
    d4 = mo.ui.dropdown(['Sexo','Contrato','Jornada','Nacemento'], value='Nacemento', label='Variable color:  ')
    return d1, d2, d3, d4, t1


@app.cell
def _(eo_matrix, epa_2d, np, referencia, t1):
    source = (
        epa_2d.groupby(["Sector", "Ocupación"], observed=True)
        .get_group(
            (eo_matrix.index[int(safe_values_row(t1))], safe_values_column(t1))
        )
        .assign(
            Idade=lambda x: [
                referencia.query('Variable=="EDAD1"').Diccionario.values[0][i]
                for i in x.EDAD
            ],
            Sexo=lambda x: [
                referencia.query('Variable=="SEXO1"').Diccionario.values[0][i]
                for i in x.SEXO1
            ],
            Situación=lambda x: [
                referencia.query('Variable=="SITU"').Diccionario.values[0][i]
                for i in x.SITU
            ],
            Contrato=lambda x: [
                referencia.query('Variable=="DUCON1"').Diccionario.values[0][i]
                if (i == "1" or i == "6")
                else np.nan
                for i in x.DUCON1
            ],
            Xornada=lambda x: [
                referencia.query('Variable=="PARCO1"').Diccionario.values[0][
                    int(i)
                ]
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
                for i in x.FORMA
            ],
            Estado_Civil=lambda x: [
                referencia.query('Variable=="ECIV1"').Diccionario.values[0][i]
                for i in x.ECIV1
            ],
            Nacemento=lambda x: np.where(
                x.PAINA1.isnull(), "España", "Estranxeiro"
            ),
        )
    )
    return (source,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Matriz Sector-Ocupación dos traballadores ocupados en Galicia en 2024
    A matriz amosa o número de traballadores ocupados en Galicia en promedio durante o ano 2024, divididos por sector (en filas) e ocupación (en columnas), a partir dos datos da *Encuesta de Población Activa* (EPA).

    Os códigos dos sectores correspóndense coa *Clasificación Nacional de Actividades Económicas* 2009 (CNAE-09), ao nivel de dous díxitos, agregados dun xeito compatible coa clasificación sectorial do Marco Input-Output de Galicia 2021 (MIOGAL-21). Os códigos das ocupacións correspóndense coa *Clasificación Nacional de Ocupaciones* 2011 (CNO-11), ao nivel de un díxito.

    Facendo *click* co cursor nunha das celas da matriz que non están baleiras, os menús situados baixo a matriz permiten desagregar o valor correspondente segundo diversos criterios.
    """
    )
    return


@app.cell
def _(cno, eo_matrix, mo, nomes, t1):
    mo.vstack(
        (
            mo.md('**'+eo_matrix.index[int(safe_values_row(t1))]+': **'+nomes['Descrición'][eo_matrix.index[int(safe_values_row(t1))]]
                + "<br>"
                 + '**'+safe_values_column(t1)+': **'+cno['Descrición'][int(safe_values_column(t1))]
            ),
            t1
        )
    )
    return


@app.cell
def _(alt, d1, d2, d3, d4, mo, source, x_labels):
    mo.hstack(
        (
            mo.vstack(
                (
                    d1,
                    d3,
                    alt.Chart(
                        source.groupby([d1.value, d3.value])
                        .Factor.sum()
                        .div(4)
                        .reset_index()
                    )
                    .mark_bar()
                    .encode(
                        alt.X(d1.value + ":N")
                        .scale(domain=x_labels[d1.value])
                        .axis(title=None, labelAngle=45),
                        alt.Y("Factor:Q").axis(title=None),
                        alt.Color(d3.value).legend(title=None),
                    )
                    .properties(height=200, width=300),
                )
            ),
            mo.vstack(
                (
                    d2,
                    d4,
                    alt.Chart(
                        source.groupby([d2.value, d4.value])
                        .Factor.sum()
                        .div(4)
                        .reset_index()
                    )
                    .mark_bar()
                    .encode(
                        alt.X(d2.value + ":N")
                        .scale(domain=x_labels[d2.value])
                        .axis(title=None, labelAngle=45),
                        alt.Y("Factor:Q").axis(title=None),
                        alt.Color(d4.value).legend(title=None),
                    )
                    .properties(height=200, width=300),
                ),
            ),
        ),
    )
    return


if __name__ == "__main__":
    app.run()
