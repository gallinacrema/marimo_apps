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
    return alt, np, pd, pyarrow


@app.cell
def _(mo):
    data_path = (
        mo.notebook_location() / "public"
    )

    design_url_epa = data_path.joinpath("dr_EPA_2021.xlsx")
    epa_g_2d = data_path.joinpath("epa_galicia_2024_2d.feather")
    cnae2009 = data_path.joinpath("cnae09.xls")
    cno2011 = data_path.joinpath("cno11.xls")
    referencia_pkl = data_path.joinpath("referencia.pkl")
    return cnae2009, cno2011, data_path, design_url_epa, epa_g_2d, referencia_pkl


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
    cnae_2d_to_miogal = {
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
                "99": "96_99",
            }
    return age_continuous_to_epa_5y_bins, cnae_2d_to_miogal, cned_2d_to_epa


@app.cell
def _(referencia_pkl):
    referencia = pd.read_pickle(referencia_pkl)
    return (referencia,)


@app.cell
def _(
    age_continuous_to_epa_5y_bins,
    cnae_2d_to_miogal,
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
        FORMA=lambda x: x.NFORMA.replace(cned_2d_to_epa),
        Sector=lambda x: x.ACT.replace(cnae_2d_to_miogal),
        Ocupación=lambda x:[i[:-1] if i!=None else i for i in x.OCUP ]
    )
    return (epa_2d,)


@app.cell
def _(epa_2d):
    epa_2d.Sector.value_counts()
    return


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
            .FACTOREL.sum().div(4).astype(int)
            .reset_index(),
            how="left",
        )
        .pivot_table(index="Sector", columns="Ocupación", values="FACTOREL")
    )
    return (eo_matrix,)


@app.cell
def safe_values_row():
    def safe_values_row(table):
        try:
            return table.value[0].row
        except IndexError:
            return '01'
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
def _(
    eo_matrix,
    epa_2d,
    np,
    referencia,
    safe_values_column,
    safe_values_row,
    t1,
):
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
                if i != None
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
    cnae = pd.read_excel(cnae2009, skiprows=2).astype('str').set_index('Unnamed: 0').to_dict()
    cno = pd.read_excel(cno2011, skiprows=2).astype('str').apply(lambda x:[i.lstrip('<b>').rstrip('</b>') for i in x]).set_index('Unnamed: 0').to_dict()
    return cnae, cno


@app.cell
def _(cnae2009, pd):
    n1 = pd.read_excel(cnae2009, skiprows=2).astype('str').rename(columns={'Unnamed: 0':'Código', 'Descrición':'Descrición rama homoxénea'}).query("Código=='03'|Código=='10'")
    return (n1,)


@app.cell
def _(pd):
    nova_fila=pd.DataFrame([{'Código':'96_99', 'Descrición rama homoxénea':'Outros servizos'}])
    n2 = pd.concat([pd.read_excel('../../Documents/Data/ABANCA/Tablas/Matriz_Simetrica_MIOGAL18.ods', sheet_name=13, header=4, usecols=[1,3], skipfooter=3), nova_fila], ignore_index=True)
    n2['Código'] = n2['Código'].str.lstrip('R').str.rstrip('M')
    n2.iloc[31,1] = 'Suministro de auga, actividades de saneamento, xestión de residuos e descontaminación'
    n2.iloc[61,1] = 'Educación'
    n2.iloc[63,1] = 'Actividades sanitarias e de servizos sociais'
    n2.iloc[65,1] = 'Actividades artísticas, recreativas e de entretemento'
    return n2, nova_fila


@app.cell
def _(n1, n2, pd):
    nomes = pd.concat([n1,n2], ignore_index=True).set_index('Código').drop(['03A','03B','10A','10B','10C','10D','10E','37_38N','85N','86_88N','90_93N','96','97']).to_dict()
    return (nomes,)


@app.cell
def _(cno, eo_matrix, mo, nomes, safe_values_column, safe_values_row, t1):
    mo.vstack(
        (
            mo.md('**'+eo_matrix.index[int(safe_values_row(t1))]+': **'+nomes['Descrición rama homoxénea'][eo_matrix.index[int(safe_values_row(t1))]]
                + "<br>"
                + '**'+safe_values_column(t1)+': **'+cno['Descrición'][safe_values_column(t1)]
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
                        .FACTOREL.sum()
                        .div(4)
                        .reset_index()
                    )
                    .mark_bar()
                    .encode(
                        alt.X(d1.value + ":N")
                        .scale(domain=x_labels[d1.value])
                        .axis(title=None, labelAngle=45),
                        alt.Y("FACTOREL:Q").axis(title=None),
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
                        .FACTOREL.sum()
                        .div(4)
                        .reset_index()
                    )
                    .mark_bar()
                    .encode(
                        alt.X(d2.value + ":N")
                        .scale(domain=x_labels[d2.value])
                        .axis(title=None, labelAngle=45),
                        alt.Y("FACTOREL:Q").axis(title=None),
                        alt.Color(d4.value).legend(title=None),
                    )
                    .properties(height=200, width=300),
                ),
            ),
        ),
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
