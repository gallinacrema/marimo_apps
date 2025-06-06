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

    filtrados = data_path.joinpath("filtrados_galicia_2d_19a24.feather")
    proxeccions_galicia = data_path.joinpath("proxeccions.feather")
    cnae2009 =  data_path.joinpath("cnae2009.feather")
    cno2011 =  data_path.joinpath("cno2011.feather")
    cnae =  data_path.joinpath("cnae_2d_to_epa.feather")
    referencia_pkl = data_path.joinpath("referencia.pkl")
    matriz =  data_path.joinpath("MIOGAL21_Simetrica.feather")
    nomes_epa = data_path.joinpath("nomes_epa.feather")
    return (
        cnae,
        cno2011,
        filtrados,
        nomes_epa,
        proxeccions_galicia,
        referencia_pkl,
    )


@app.cell
def _(cnae, cno2011, nomes_epa, pd, referencia_pkl):
    referencia = pd.read_pickle(referencia_pkl)
    cnae_2d_to_epa = pd.read_feather(cnae).to_dict()['Nuevo_codigo']
    cno = pd.read_feather(cno2011).astype('str').apply(lambda x:[i.lstrip('<b>').rstrip('</b>') for i in x])
    nomes = pd.read_feather(nomes_epa).set_index('Código').to_dict()
    return cnae_2d_to_epa, cno, nomes


@app.cell
def _(filtrados, pd):
    base = pd.read_feather(filtrados).reset_index().rename(columns={'index':'ID'})
    return (base,)


@app.cell
def _(base):
    xubilados = base.query('(SIDI1=="02"|SIDI2=="02"|SIDI3=="02")&DTANT<4&(AOI!="03"&AOI!="04")').ID.values
    return (xubilados,)


@app.cell
def _(base, cnae_2d_to_epa, np, xubilados):
    df = base.assign(
        XUBIL=lambda x: [i in xubilados for i in x.ID],
        Sector=lambda x: np.where(
            x.XUBIL == True,
            x.ACTA.astype("str").replace(cnae_2d_to_epa),
            x.ACT.astype("str").replace(cnae_2d_to_epa),
        ),
        Ocupacion=lambda x: np.where(x.XUBIL == True, x.OCUPA.astype("str"), x.OCUP.astype("str")),
    ).astype({"XUBIL": int, "Sector": str})
    return (df,)


@app.cell
def _(df):
    df_maiores = (
        df.query('EDAD1>50&Sector!="nan"')
        .groupby(["CICLO", "Sector", "Ocupacion", "EDAD1", "XUBIL"])
        .Factor.sum()
        .round()
        .reset_index()
    )
    return (df_maiores,)


@app.cell
def _():
    anos_futuros=["2025","2026","2027","2028","2029","2030"]
    return (anos_futuros,)


@app.cell
def _(df):
    ocupados = df.query('AOI=="03"|AOI=="04"').assign(Ocup=lambda x:[i[:-1] for i in x.Ocupacion])
    return


@app.cell
def _(df):
    xubilados_24 = df.query('(CICLO=="202"|CICLO=="203"|CICLO=="204"|CICLO=="205")&XUBIL==1')
    return (xubilados_24,)


@app.cell
def _(df):
    ocupados_24 = df.query('(CICLO=="202"|CICLO=="203"|CICLO=="204"|CICLO=="205")&(AOI=="03"|AOI=="04")')
    return (ocupados_24,)


@app.cell
def _(xubilados_24):
    xub24_idade = (
        xubilados_24.query("EDAD1>50")
        .groupby(["Sector", "Ocupacion", "EDAD1"])
        .Factor.sum()
        .div(4)
        .round()
        .reset_index()
    )
    return (xub24_idade,)


@app.cell
def _(ocupados_24):
    ocup24_idade = (
        ocupados_24.query("EDAD1>50")
        .groupby(["Sector", "Ocupacion", "EDAD1"])
        .Factor.sum()
        .div(4)
        .round()
        .reset_index()
    )
    return (ocup24_idade,)


@app.cell
def _(df_maiores, np):
    def porcentaxe(sector, ocupacion):
        return (
            df_maiores.query(
                'XUBIL==1'
            )
            .groupby(["EDAD1"])
            .Factor.sum()
            .reset_index()
            .merge(
                df_maiores.query(
                'XUBIL==0'
            )
                .groupby(["EDAD1"])
                .Factor.sum()
                .reset_index(),
                on="EDAD1",
                how='left'
            )
            .assign(
                p_media=lambda x: (
                    x.Factor_x * 100 / (x.Factor_x + x.Factor_y)
                ).round(1)
            )
                .drop(['Factor_x','Factor_y'], axis=1)
            .merge((df_maiores.query(
                f'Sector=="{sector}"&Ocupacion=="{ocupacion}"&XUBIL==1'
            )
            .groupby(["EDAD1"])
            .Factor.sum()
            .reset_index()
            .merge(
                df_maiores.query(f'Sector=="{sector}"&Ocupacion=="{ocupacion}"&XUBIL==0')
                .groupby(["EDAD1"])
                .Factor.sum()
                .reset_index(),
                on="EDAD1",
                how='outer'
            )
                .fillna(0)
           .assign(
                p_esp=lambda x: (
                    x.Factor_x * 100 / (x.Factor_x + x.Factor_y)
                ).round(1)
            )
                   ), on='EDAD1'
                  )
            .rename(columns={"EDAD1": "Idade"})
                   .assign(Porcentaxe=lambda x:np.where(x.p_esp<x.p_media,x.p_media,x.p_esp))
            .filter(['Idade','Porcentaxe'])
        )
    return (porcentaxe,)


@app.cell
def _(anos_futuros, ocup24_idade, pd, porcentaxe, xub24_idade):
    def proxeccion(sector, ocupacion):
        return pd.DataFrame(
            {
                j: ocup24_idade.query(
                    f'Sector=="{sector}"&Ocupacion=="{ocupacion}"'
                )
                .groupby(["EDAD1"])
                .Factor.sum()
                .reset_index()
                .merge(
                    xub24_idade.query(
                        f'Sector=="{sector}"&Ocupacion=="{ocupacion}"'
                    )
                    .groupby(["EDAD1"])
                    .Factor.sum()
                    .reset_index(),
                    on="EDAD1",
                    how="left",
                )
                .fillna(0)
                .assign(
                    Restantes=lambda x: (x.Factor_x - x.Factor_y),
                    Idade=lambda x: x.EDAD1 + int(j) - 2024,
                )
                .drop(["Factor_x", "Factor_y"], axis=1)
                .merge(porcentaxe(sector, ocupacion), on="Idade")
                .assign(
                    Xubilados=lambda x: (x.Restantes * x.Porcentaxe / 100).round()
                )
                .Xubilados.sum()
                for j in anos_futuros
            },
            index=["Xubilacións"],
        )
    return (proxeccion,)


@app.cell
def _(pd, proxeccions_galicia):
    proxys = pd.read_feather(proxeccions_galicia)
    return (proxys,)


@app.cell
def _(np, pd, proxys):
    matrix = (pd.DataFrame(np.array(
                np.meshgrid(
                    np.sort(proxys.Sector.unique()),
                    np.sort([str(i) for i in range(10)]),
                )
            ).T.reshape(-1, 2),
                 columns=["Sector", "Ocup"]
                ).merge(
            proxys.assign(Ocup=lambda x:[i[:-1] for i in x.Ocupacion]).groupby(['Sector','Ocup']).Proxección.sum().reset_index(),
            how="left",
        )
        .pivot_table(index="Sector", columns="Ocup", values="Proxección")
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
def _(matrix, mo):
    t1 = mo.ui.table(matrix, selection='single-cell', show_column_summaries=False, pagination=False)
    return (t1,)


@app.cell
def _(anos_futuros, df, matrix, np, pd, proxeccion, t1):
    try:
        resumo = (
            pd.concat(
                [
                    proxeccion(matrix.index[int(safe_values_row(t1))], i)
                    for i in [
                        i
                        for i in np.sort(
                            df.query(
                                f'Sector=="{matrix.index[int(safe_values_row(t1))]}"&Ocupacion!="nan"'
                            ).Ocupacion.unique()
                        )
                        if i[:-1] == safe_values_column(t1)
                    ]
                ]
            )
            .sum()
            .reset_index()
            .rename(columns={"index": "Ano", 0: "valor"})
        )

    except ValueError:
        resumo = pd.DataFrame(zip(anos_futuros, [0] * 6), columns=["Ano", "valor"])
    return (resumo,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Proxección das xubilacións futuras en Galicia (2025-2030)
    A táboa amosa a estimación do número de traballadores ocupados en Galicia en 2024 que se xubilarán no período 2025-2030, divididos por sector (en filas) e ocupación (en columnas), a partir dos datos da *Encuesta de Población Activa* (EPA).

    Os códigos dos sectores correspóndense coa *Clasificación Nacional de Actividades Económicas* 2009 (CNAE-09), ao nivel de dous díxitos, agregados dun xeito compatible coa clasificación sectorial do Marco Input-Output de Galicia 2021 (MIOGAL-21). Os códigos das ocupacións correspóndense coa *Clasificación Nacional de Ocupaciones* 2011 (CNO-11), ao nivel de un díxito.

    Facendo *click* co cursor nunha das celas da táboa que non teñan un valor igual a cero, o gráfico situado debaixo da tabla amosará a distribución das xubilacións ano a ano, e a pequena tabla á dereita do gráfico amosará a desagregación das xubilacións por tipo de ocupación ao nivel de dos díxitos da CNO-11.
    """
    )
    return


@app.cell
def _(cno, matrix, mo, nomes, t1):
    mo.vstack(
        (
            mo.md('**'+matrix.index[int(safe_values_row(t1))]+': **'+nomes['Descrición'][matrix.index[int(safe_values_row(t1))]]
                + "<br>"
                + '**'+safe_values_column(t1)+': **'+cno.query(f"`Unnamed: 0`=='{safe_values_column(t1)}'").Descrición.values[0]
            ),
            t1,
            )
        )
    return


@app.cell
def _(alt, df, matrix, mo, np, pd, proxeccion, resumo, t1):
    mo.vstack(
            (
                mo.vstack(
                    (
                        mo.md("Total xubilacións previstas 2025-2030:"),
                        resumo.valor.sum().astype(int),
                    )
                ),
                mo.hstack(
                    (
                        alt.Chart(resumo)
                        .mark_bar(size=25)
                        .encode(
                            alt.X("Ano").title(None).axis(labelAngle=0),
                            alt.Y("valor").title(None),
                        )
                        .properties(width=360, height=200),
                        pd.DataFrame(
                            {
                                i: proxeccion(
                                    matrix.index[int(safe_values_row(t1))], i
                                ).sum(axis=1)
                                for i in [
                                    i
                                    for i in np.sort(
                                        df.query(
                                            f'Sector=="{matrix.index[int(safe_values_row(t1))]}"&Ocupacion!="nan"'
                                        ).Ocupacion.unique()
                                    )
                                    if i[:-1] == safe_values_column(t1)
                                ]
                            }
                        ),
                    )
                ),
            )
        )
    return


if __name__ == "__main__":
    app.run()
