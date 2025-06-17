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

    xubilados_galicia = data_path.joinpath("xubilados_galicia_19a24.feather")
    cnae2009 =  data_path.joinpath("cnae2009.feather")
    cno2011 =  data_path.joinpath("cno2011.feather")
    cnae =  data_path.joinpath("cnae_2d_to_epa.feather")
    cned =  data_path.joinpath("cned_2d_to_epa.feather")
    referencia_pkl = data_path.joinpath("referencia.pkl")
    matriz =  data_path.joinpath("MIOGAL21_Simetrica.feather")
    nomes_epa = data_path.joinpath("nomes_epa.feather")
    return (
        cnae,
        cnae2009,
        cned,
        cno2011,
        nomes_epa,
        referencia_pkl,
        xubilados_galicia,
    )


@app.cell
def _(cnae, cned, cno2011, nomes_epa, pd, referencia_pkl):
    referencia = pd.read_pickle(referencia_pkl)
    cnae_2d_to_epa = pd.read_feather(cnae).to_dict()['Nuevo_codigo']
    cned_2d_to_epa = pd.read_feather(cned).to_dict()['Nuevo_codigo']
    cno = pd.read_feather(cno2011).astype('str').apply(lambda x:[i.lstrip('<b>').rstrip('</b>') for i in x])
    nomes = pd.read_feather(nomes_epa).set_index('Código').to_dict()
    return cnae_2d_to_epa, cned_2d_to_epa, cno, nomes, referencia


@app.cell
def _(cnae_2d_to_epa, pd, xubilados_galicia):
    xubilados = pd.read_feather(xubilados_galicia).assign(Sector=lambda x:x.ACTA.astype('str').replace(cnae_2d_to_epa).astype('category'), Ocupación=lambda x:[i[:-1] for i in x.OCUPA])
    return (xubilados,)


@app.cell
def _(cnae2009, cnae_2d_to_epa, np, pd):
    sectores = (
        pd.read_feather(cnae2009)
        .astype("str")
        .rename(columns={"Unnamed: 0": "CNAE"})
        .assign(CNAE_2D=lambda x: [i if len(i) == 2 else np.nan for i in x.CNAE])
        .dropna()
        .reset_index()
        .drop(["index", "Descrición", "CNAE_2D"], axis=1)
        .merge(
            pd.DataFrame(cnae_2d_to_epa, index=["Codigo"])
            .T.reset_index()
            .rename(columns={"index": "CNAE"}), how='outer'
        )
    )
    return (sectores,)


@app.cell
def _(sectores):
    sectores.Codigo = sectores.Codigo.fillna(sectores.CNAE)
    return


@app.cell
def _(np, pd, sectores, xubilados):
    matrix = (
        pd.DataFrame(
            np.array(
                np.meshgrid(
                    np.sort(sectores.Codigo.unique()),
                    np.array(['0','1','2','3','4','5','6','7','8','9']),
                )
            ).T.reshape(-1, 2),
            columns=["Sector", "Ocupación"],
        )
        .merge(
            xubilados.groupby(["Sector", "Ocupación"], observed=True)
            .Factor.sum().round()
            .reset_index(),
            how="left",
        )
        .pivot_table(index="Sector", columns="Ocupación", values="Factor")
    )
    return (matrix,)


@app.function
def safe_values_row(table):
    try:
        return table.value[0].row
    except IndexError:
        return '0'


@app.function
def safe_values_column(table):
    try:
        return table.value[0].column
    except IndexError:
        return '6'


@app.cell
def _(referencia):
    x_labels = {
        "Data": [str(2019+(i-186)//4) for i in range(186,210)],
        "Idade": ["55 ou menos"] + list(range(56, 76)) + ["Máis de 75"],
        "Formación": [
            "Analfabetos",
            "Primaria incompleta",
            "Primaria",
            "ESO",
            "Bachiller",
            "FP",
            "Superior",
        ],
        "Situación": list(
            referencia.query('Variable=="SITUA"').Diccionario.values[0].values()
        ),
        "Estado_Civil": list(
            referencia.query('Variable=="ECIV1"').Diccionario.values[0].values()
        ),
    }
    return (x_labels,)


@app.cell
def _(matrix, mo):
    t1 = mo.ui.table(matrix, selection='single-cell', show_column_summaries=False, pagination=False)
    d1 = mo.ui.dropdown(['Data','Idade','Formación','Situación','Estado_Civil'], value='Data', label='Variable eixo horizontal:  ')
    d2 = mo.ui.dropdown(['Data','Idade','Formación','Situación','Estado_Civil'], value='Idade', label='Variable eixo horizontal:  ')
    d3 = mo.ui.dropdown(['Sexo','Nacemento'], value='Sexo', label='Variable color:  ')
    d4 = mo.ui.dropdown(['Sexo','Nacemento'], value='Nacemento', label='Variable color:  ')
    return d1, d2, d3, d4, t1


@app.cell
def _(cned_2d_to_epa, matrix, np, referencia, t1, xubilados):
    source = (
        xubilados.groupby(["Sector", "Ocupación"], observed=True)
        .get_group(
            (matrix.index[int(safe_values_row(t1))], safe_values_column(t1))
        )
        .assign(
            Data=lambda x:[str(2019+(i-186)//4) for i in x.CICLO.astype(int)],
            Idade=lambda x: x.EDAD1.astype(int).replace({
        50:"55 ou menos",
        51:"55 ou menos",
        53:"55 ou menos",
        54:"55 ou menos",
        55:"55 ou menos",
        76:"Máis de 75",
        78:"Máis de 75",
        80:"Máis de 75",
        81:"Máis de 75",
        83:"Máis de 75",
        84:"Máis de 75",
    }),
            Sexo=lambda x: [
                referencia.query('Variable=="SEXO1"').Diccionario.values[0][i]
                for i in x.SEXO1
            ],
            Situación=lambda x: [
                referencia.query('Variable=="SITUA"').Diccionario.values[0][i]
                if len(i) == 2
                else referencia.query('Variable=="SITUA"').Diccionario.values[0][
                    "0" + i
                ]
                for i in x.SITUA
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
                for i in x.NFORMA.astype('str').replace(cned_2d_to_epa).astype('category')
            ],
            Estado_Civil=lambda x: [
                referencia.query('Variable=="ECIV1"').Diccionario.values[0][i]
                for i in x.ECIV1
            ],
            Nacemento=lambda x: np.where(
                x.PAINA1.isnull(), "España", "Extranjero"
            ),
        )
    )
    return (source,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Traballadores ocupados que se xubilaron en Galicia (2019-2024)
    A táboa amosa o número de traballadores ocupados en Galicia que se xubilaron no período 2019-2024, divididos por sector (en filas) e ocupación (en columnas), a partir dos datos da *Encuesta de Población Activa* (EPA).

    Os códigos dos sectores correspóndense coa *Clasificación Nacional de Actividades Económicas* 2009 (CNAE-09), ao nivel de dous díxitos, agregados dun xeito compatible coa clasificación sectorial do Marco Input-Output de Galicia 2021 (MIOGAL-21). Os códigos das ocupacións correspóndense coa *Clasificación Nacional de Ocupaciones* 2011 (CNO-11), ao nivel de un díxito.

    Facendo *click* co cursor nunha das celas da táboa que non están baleiras, os menús situados baixo a matriz permiten desagregar o valor correspondente segundo diversos criterios.
    """
    )
    return


@app.cell
def _(alt, cno, d1, d2, d3, d4, matrix, mo, nomes, source, t1, x_labels):
    mo.vstack((mo.vstack(
        (
            mo.md('**'+matrix.index[int(safe_values_row(t1))]+': **'+nomes['Descrición'][matrix.index[int(safe_values_row(t1))]]
                + "<br>"
                + '**'+safe_values_column(t1)+': **'+cno['Descrición'][int(safe_values_column(t1))]
            ),
            t1
        )
    ),
               mo.hstack(
        (
            mo.vstack(
                (
                    d1,
                    d3,
                    alt.Chart(
                        source.groupby([d1.value, d3.value])
                        .Factor.sum()
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
              )
             )
    return


if __name__ == "__main__":
    app.run()
