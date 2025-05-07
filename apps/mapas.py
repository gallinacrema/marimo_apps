import marimo

__generated_with = "0.13.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import pandas as pd
    import altair as alt
    import geopandas as gpd
    return alt, gpd, pd


@app.cell
def _(mo):
    data_path = (
            mo.notebook_location() / "public"
        )

    shapefiles = data_path.joinpath("Concellos_IGN.shp")
    ratios = data_path.joinpath("ratio.xlsx")
    return ratios, shapefiles


@app.cell
def _(gpd, pd, ratios, shapefiles):
    concellos = (
        gpd.read_file(shapefiles)
        .filter(["CODIGOINE", "geometry"])
        .merge(
            pd.read_excel(ratios, header=2).assign(
                CODIGOINE=lambda x: x.loc[:, "Codigo Municipio"].astype("str"),
                Total=lambda x: x.TOTAL.round(1),
                Menores_45=lambda x: x.loc[:, "MENOR-45"].round(1),
            )
            .filter(['CODIGOINE',' Municipio','Total', 'Menores_45'])
        )
    )
    return (concellos,)


@app.cell
def _(mo):
    d1 = mo.ui.dropdown(['Total', 'Menores_45'],value='Total')
    return (d1,)


@app.cell
def _(alt, concellos):
    basemap = alt.Chart(concellos).mark_geoshape(
                stroke='black',
                strokeOpacity=.05
            ).encode(
                shape='geometry:G'
            ).transform_lookup(
                lookup='CODIGOINE',
                from_=alt.LookupData(data=concellos, key='CODIGOINE'),
                as_='geometry'
            ).properties(
                width=600,
                height=450
    )
    return (basemap,)


@app.cell
def _(alt, basemap, d1):
    mapa = basemap.encode(
                color=alt.Color(f'{d1.value}:Q', legend=alt.Legend(title=None), scale=alt.Scale(scheme='greenblue')),
                tooltip=alt.Tooltip([' Municipio:N', f'{d1.value}:Q'])
            )
    return (mapa,)


@app.cell
def _(d1, mapa, mo):
    mo.hstack((d1, mapa))
    return


if __name__ == "__main__":
    app.run()
