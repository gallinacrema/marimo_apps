import marimo

__generated_with = "0.13.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import altair as alt
    import geopandas as gpd
    return alt, gpd


@app.cell
def _(mo):
    data_path = (
            mo.notebook_location() / "public"
        )

    shapefiles = data_path.joinpath("ratio_concellos_galicia.shp")
    return (shapefiles,)


@app.cell
def _(gpd, shapefiles):
    datos = gpd.read_file(shapefiles, engine="pyogrio")
    return (datos,)


@app.cell
def _(mo):
    d1 = mo.ui.dropdown(['Total', 'Menores_45'],value='Total')
    return (d1,)


@app.cell
def _(alt, datos):
    basemap = alt.Chart(datos).mark_geoshape(
                stroke='black',
                strokeOpacity=.05
            ).encode(
                shape='geometry:G'
            ).transform_lookup(
                lookup='CODIGOINE',
                from_=alt.LookupData(data=datos, key='CODIGOINE'),
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
