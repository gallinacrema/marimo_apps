import marimo

__generated_with = "0.13.4"
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

    epa_g_2d = data_path.joinpath("epa_galicia_2024_2d.feather")
    cnae2009 = data_path.joinpath("cnae.feather")
    cno2011 = data_path.joinpath("cno.feather")
    referencia_pkl = data_path.joinpath("referencia.pkl")
    matriz =  data_path.joinpath("MIOGAL21_Simetrica.feather")
    return cnae2009, cno2011, epa_g_2d, matriz, referencia_pkl


@app.cell
def _():
    age_continuous_to_epa_5y_bins = [0, 4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54, 59, 64, 109]
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
    cnae_2d_to_epa = {
        "07": "05_09",
        "08": "05_09",
        "09": "05_09",
        "11": "11_12",
        "12": "11_12",
        "13": "13_15",
        "14": "13_15",
        "15": "13_15",
        "17": "17_22",
        "19": "17_22",
        "20": "17_22",
        "21": "17_22",
        "22": "17_22",
        "24": "24_25",
        "25": "24_25",
        "26": "26_28",
        "27": "26_28",
        "28": "26_28",
        "35": "35_39",
        "36": "35_39",
        "37": "35_39",
        "38": "35_39",
        "39": "35_39",
        "41": "41_43",
        "42": "41_43",
        "43": "41_43",
        "49": "49_51",
        "50": "49_51",
        "51": "49_51",
        "58": "58_60",
        "59": "58_60",
        "60": "58_60",
        "61": "61_63",
        "62": "61_63",
        "63": "61_63",
        "64": "64_66",
        "65": "64_66",
        "66": "64_66",
        "69": "69_75",
        "70": "69_75",
        "71": "69_75",
        "72": "69_75",
        "73": "69_75",
        "74": "69_75",
        "75": "69_75",
        "77": "77_82",
        "78": "77_82",
        "79": "77_82",
        "80": "77_82",
        "81": "77_82",
        "82": "77_82",
        "86": "86_88",
        "87": "86_88",
        "88": "86_88",
        "90": "90_93",
        "91": "90_93",
        "92": "90_93",
        "93": "90_93",
        "94": "94_99",
        "95": "94_99",
        "96": "94_99",
        "97": "94_99",
        "99": "94_99",
    }
    return age_continuous_to_epa_5y_bins, cnae_2d_to_epa, cned_2d_to_epa


@app.cell
def _(pd, referencia_pkl):
    referencia = pd.read_pickle(referencia_pkl)
    return (referencia,)


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
                    epa_2d.query(
                        'AOI=="03"|AOI=="04"'
                    ).Sector.unique(),
                    epa_2d.query(
                        'AOI=="03"|AOI=="04"'
                    ).Ocupación.unique(),
                )
            ).T.reshape(-1, 2),
            columns=["Sector", "Ocupación"],
        )
        .merge(
            epa_2d.query(
                'AOI=="03"|AOI=="04"'
            )
            .groupby(["Sector", "Ocupación"], observed=True)
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
    x_labels = {'Edad': list(referencia.query('Variable=="EDAD1"').Diccionario.values[0].values()),
                'Formación': ["Analfabetos", "Primaria incompleta", "Primaria", "ESO", "Bachiller", "FP", "Superior"],
                'Situación': list(referencia.query('Variable=="SITU"').Diccionario.values[0].values()),
                'Estado_Civil': list(referencia.query('Variable=="ECIV1"').Diccionario.values[0].values())
               }
    return (x_labels,)


@app.cell
def _(eo_matrix, mo):
    t1 = mo.ui.table(eo_matrix, selection='single-cell', show_column_summaries=False, pagination=False)
    d1 = mo.ui.dropdown(['Edad','Formación','Situación','Estado_Civil'], value='Edad', label='Variable eje horizontal:  ')
    d2 = mo.ui.dropdown(['Edad','Formación','Situación','Estado_Civil'], value='Formación', label='Variable eje horizontal:  ')
    d3 = mo.ui.dropdown(['Sexo','Contrato','Jornada','Nacimiento'], value='Sexo', label='Variable color:  ')
    d4 = mo.ui.dropdown(['Sexo','Contrato','Jornada','Nacimiento'], value='Sexo', label='Variable color:  ')
    return d1, d2, d3, d4, t1


@app.cell
def _(eo_matrix, epa_2d, np, referencia, t1):
    source = (
        epa_2d.groupby(["Sector", "Ocupación"], observed=True)
        .get_group(
            (eo_matrix.index[int(safe_values_row(t1))], safe_values_column(t1))
        )
        .assign(
            Edad=lambda x: [
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
            Jornada=lambda x: [
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
            Nacimiento=lambda x: np.where(
                x.PAINA1.isnull(), "España", "Extranjero"
            ),
        )
    )
    return (source,)


@app.cell
def _(cnae2009, cno2011, pd):
    cnae = pd.read_feather(cnae2009).to_dict()
    cno = pd.read_feather(cno2011).to_dict()
    return (cno,)


@app.cell
def _(cnae2009, pd):
    n1 = (
        pd.read_feather(cnae2009)
        .astype("str")
        .rename(columns={"Unnamed: 0": "Código"})
        .query("Código=='03'|Código=='10'")
    )
    novas = pd.DataFrame(
        {
            0: {
                "Código": "13_15",
                "Descrición": "Téxtil, confección, coiro e calzado",
            },
            1: {"Código": "17_22", "Descrición": "Industrias químicas"},
            2: {
                "Código": "24_25",
                "Descrición": "Metalurxia e produtos metálicos",
            },
            3: {
                "Código": "26_28",
                "Descrición": "Maquinaria, equipamento produtos eléctricos e electrónicos",
            },
            4: {"Código": "35_39", "Descrición": "Enerxía, auga e saneamento"},
            5: {"Código": "64_66", "Descrición": "Actividades financeiras e de seguros"},
            6: {"Código": "49_51", "Descrición": "Transporte"},
            7: {
                "Código": "58_60",
                "Descrición": "Actividades cinematográficas de video e televisión, gravación de son e edición",
            },
            8: {
                "Código": "69_75",
                "Descrición": "Actividades profesionais, científicas e técnicas",
            },
            9: {
                "Código": "61_63",
                "Descrición": "Telecomunicacións e informática",
            },
            10: {
                "Código": "77_82",
                "Descrición": "Actividades administrativas e servizos auxiliares",
            },
        }
    ).T
    return n1, novas


@app.cell
def _(matriz, pd):
    nova_fila=pd.DataFrame([{'Código':'94_99', 'Descrición rama homoxénea':'Outros servizos'}])
    n2 = pd.concat([pd.read_feather(matriz), nova_fila], ignore_index=True).rename(columns={'Descrición rama homoxénea':'Descrición'})
    n2['Código'] = n2['Código'].str.lstrip('R').str.rstrip('M')
    n2.iloc[31,1] = 'Suministro de auga, actividades de saneamento, xestión de residuos e descontaminación'
    n2.iloc[61,1] = 'Educación'
    n2.iloc[63,1] = 'Actividades sanitarias e de servizos sociais'
    n2.iloc[65,1] = 'Actividades artísticas, recreativas e de entretemento'
    n2.iloc[65,0] = '90_93'
    return (n2,)


@app.cell
def _(n1, n2, novas, pd):
    nomes = (
        pd.concat([n1, novas, n2], ignore_index=True)
        .set_index("Código")
        .drop(
            [
                "03A",
                "03B",
                "10A",
                "10B",
                "10C",
                "10D",
                "10E",
                "37_38N",
                "85N",
                "86_88N",
                "93",
                "96",
                "97",
                "13",
                "14_15",
                "17",
                "18",
                "19",
                "20_21",
                "22",
                "24",
                "25",
                "26",
                "27",
                "28",
                "35",
                "36_39",
                "49",
                "50_51",
                "58",
                "59_60",
                "61",
                "64",
                "65",
                "66",
                "69_70",
                "71",
                "72",
                "73",
                "74_75",
                "77",
                "78",
                "79",
                "80_82",
                "94",
                "95",
            ]
        )
        .to_dict()
    )
    return (nomes,)


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
