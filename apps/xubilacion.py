import marimo

__generated_with = "0.12.6"
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
    return pyarrow, alt, np, pd


@app.cell
def _(mo):
    data_path = (
        mo.notebook_location() / "public"
    )

    xubilados_galicia = data_path.joinpath("xubilados_galicia_19a24.feather")
    cnae2009 = data_path.joinpath("cnae.feather")
    cno2011 = data_path.joinpath("cno.feather")
    referencia_pkl = data_path.joinpath("referencia.pkl")
    matriz =  data_path.joinpath("MIOGAL21_Simetrica.feather")
    return (
        cnae2009,
        cno2011,
        data_path,
        referencia_pkl,
        matriz,
        xubilados_galicia,
    )


@app.cell
def _(pd, referencia_pkl):
    referencia = pd.read_pickle(referencia_pkl)
    return (referencia,)


@app.cell
def _(cnae_2d_to_miogal, pd, xubilados_galicia):
    xubilados = pd.read_feather(xubilados_galicia).assign(Sector=lambda x:x.ACTA.replace(cnae_2d_to_miogal), Ocupación=lambda x:[i[:-1] for i in x.OCUPA])
    return (xubilados,)


@app.cell
def _():
    cned_2d_to_epa = {
        "01": "AN",
        "02": "P1",
        "10": "P2",
        "21": "S1",
        "22": "S1",
        "23": "SP",
        "24": "SP",
        "32": "SG",
        "33": "SP",
        "34": "SP",
        "35": "SP",
        "38": "SP",
        "41": "SP",
        "51": "SU",
        "52": "SU",
        "61": "SU",
        "62": "SU",
        "63": "SU",
        "71": "SU",
        "72": "SU",
        "73": "SU",
        "74": "SU",
        "75": "SU",
        "81": "SU",
    }
    cnae_2d_to_miogal = {
        "05": "05_09",
        "06": "05_09",
        "07": "05_09",
        "08": "05_09",
        "09": "05_09",
        "11": "11_12",
        "12": "11_12",
        "14": "14_15",
        "15": "14_15",
        "20": "20_21",
        "21": "20_21",
        "36": "36_39",
        "37": "36_39",
        "38": "36_39",
        "39": "36_39",
        "41": "41_43",
        "42": "41_43",
        "43": "41_43",
        "50": "50_51",
        "51": "50_51",
        "59": "59_60",
        "60": "59_60",
        "62": "62_63",
        "63": "62_63",
        "69": "69_70",
        "70": "69_70",
        "74": "74_75",
        "75": "74_75",
        "80": "80_82",
        "81": "80_82",
        "82": "80_82",
        "86": "86_88",
        "87": "86_88",
        "88": "86_88",
        "90": "90_93",
        "91": "90_93",
        "92": "90_93",
        "93": "90_93",
        "96": "96_99",
        "97": "96_99",
        "98": "96_99",
        "99": "96_99",
    }
    edades = {
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
    }
    ciclo_to_data = {
        186:"1T 2019",
        187:"2T 2019",
        188:"3T 2019",
        189:"4T 2019",
        190:"1T 2020",
        191:"2T 2020",
        192:"3T 2020",
        193:"4T 2020",
        194:"1T 2021",
        195:"2T 2021",
        196:"3T 2021",
        197:"4T 2021",
        198:"1T 2022",
        199:"2T 2022",
        200:"3T 2022",
        201:"4T 2022",
        202:"1T 2023",
        203:"2T 2023",
        204:"3T 2023",
        205:"4T 2023",
        206:"1T 2024",
        207:"2T 2024",
        208:"3T 2024",
        209:"4T 2024",
    }
    return ciclo_to_data, cnae_2d_to_miogal, cned_2d_to_epa, edades


@app.cell
def _(cnae2009, cnae_2d_to_miogal, np, pd):
    sectores = (
        pd.read_excel(cnae2009, skiprows=2)
        .astype("str")
        .rename(columns={"Unnamed: 0": "CNAE"})
        .assign(CNAE_2D=lambda x: [i if len(i) == 2 else np.nan for i in x.CNAE])
        .dropna()
        .reset_index()
        .drop(["index", "Descrición", "CNAE_2D"], axis=1)
        .merge(
            pd.DataFrame(cnae_2d_to_miogal, index=["Codigo"])
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


@app.cell
def safe_values_row():
    def safe_values_row(table):
        try:
            return table.value[0].row
        except IndexError:
            return '23'
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
def _(referencia):
    x_labels = {
        "Data": [
            "1T 2019",
            "2T 2019",
            "3T 2019",
            "4T 2019",
            "1T 2020",
            "2T 2020",
            "3T 2020",
            "4T 2020",
            "1T 2021",
            "2T 2021",
            "3T 2021",
            "4T 2021",
            "1T 2022",
            "2T 2022",
            "3T 2022",
            "4T 2022",
            "1T 2023",
            "2T 2023",
            "3T 2023",
            "4T 2023",
            "1T 2024",
            "2T 2024",
            "3T 2024",
            "4T 2024",       
        ],
        "Idade": [
            "55 ou menos",
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            "Máis de 75",
        ],
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
    d1 = mo.ui.dropdown(['Data','Idade','Formación','Situación','Estado_Civil'], value='Data', label='Variable eje horizontal:  ')
    d2 = mo.ui.dropdown(['Data','Idade','Formación','Situación','Estado_Civil'], value='Idade', label='Variable eje horizontal:  ')
    d3 = mo.ui.dropdown(['Sexo','Nacemento'], value='Sexo', label='Variable color:  ')
    d4 = mo.ui.dropdown(['Sexo','Nacemento'], value='Nacemento', label='Variable color:  ')
    return d1, d2, d3, d4, t1


@app.cell
def _(
    ciclo_to_data,
    cned_2d_to_epa,
    edades,
    matrix,
    np,
    referencia,
    safe_values_column,
    safe_values_row,
    t1,
    xubilados,
):
    source = (
        xubilados.groupby(["Sector", "Ocupación"], observed=True)
        .get_group(
            (matrix.index[int(safe_values_row(t1))], safe_values_column(t1))
        )
        .assign(
            Data=lambda x:x.CICLO.astype(int).replace(ciclo_to_data),
            Idade=lambda x: x.EDAD1.astype(int).replace(edades),
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
                for i in x.NFORMA.replace(cned_2d_to_epa)
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
def _(cnae2009, cno2011, pd):
    cnae = pd.read_excel(cnae2009, skiprows=2).astype('str').set_index('Unnamed: 0').to_dict()
    cno = pd.read_excel(cno2011, skiprows=2).astype('str').apply(lambda x:[i.lstrip('<b>').rstrip('</b>') for i in x]).set_index('Unnamed: 0').to_dict()
    return cnae, cno


@app.cell
def _(cnae2009, pd):
    n1 = pd.read_excel(cnae2009, skiprows=2).astype('str').rename(columns={'Unnamed: 0':'Código', 'Descrición':'Descrición rama homoxénea'}).query("Código=='03'|Código=='10'")
    return (n1,)


@app.cell
def _(matriz, pd):
    nova_fila=pd.DataFrame([{'Código':'96_99', 'Descrición rama homoxénea':'Outros servizos'}])
    n2 = pd.concat([pd.read_excel(matriz, sheet_name=13, header=4, usecols=[1,3], skipfooter=3), nova_fila], ignore_index=True)
    n2['Código'] = n2['Código'].str.lstrip('R').str.rstrip('M')
    n2.iloc[31,1] = 'Suministro de auga, actividades de saneamento, xestión de residuos e descontaminación'
    n2.iloc[61,1] = 'Educación'
    n2.iloc[63,1] = 'Actividades sanitarias e de servizos sociais'
    n2.iloc[65,1] = 'Actividades artísticas, recreativas e de entretemento'
    n2.iloc[65,0] = '90_93'
    return n2, nova_fila


@app.cell
def _(n1, n2, pd):
    nomes = pd.concat([n1,n2], ignore_index=True).set_index('Código').drop(['03A','03B','10A','10B','10C','10D','10E','37_38N','85N','86_88N','93','96','97']).to_dict()
    return (nomes,)


@app.cell
def _(
    alt,
    cno,
    d1,
    d2,
    d3,
    d4,
    matrix,
    mo,
    nomes,
    safe_values_column,
    safe_values_row,
    source,
    t1,
    x_labels,
):
    mo.hstack((mo.vstack(
        (
            mo.md('**'+matrix.index[int(safe_values_row(t1))]+': **'+nomes['Descrición rama homoxénea'][matrix.index[int(safe_values_row(t1))]]
                + "<br>"
                + '**'+safe_values_column(t1)+': **'+cno['Descrición'][safe_values_column(t1)]
            ),
            t1
        )
    ),
               mo.vstack(
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
