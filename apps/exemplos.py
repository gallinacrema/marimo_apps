import marimo

__generated_with = "0.13.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import pandas as pd
    return (pd,)


@app.cell
def _(mo):
    data_path = (
        mo.notebook_location() / "public"
    )

    xubilados_galicia = data_path.joinpath("xubilados_galicia_19a24.feather")
    cnae2009 =  data_path.joinpath("cnae.feather")
    cno2011 =  data_path.joinpath("cno.feather")
    referencia_pkl = data_path.joinpath("referencia.pkl")
    epa_g_2d = data_path.joinpath("epa_galicia_2d_19a24.feather")
    return epa_g_2d, xubilados_galicia


@app.cell
def _():
    ciclo_to_años = {
        186:"2019",
        187:"2019",
        188:"2019",
        189:"2019",
        190:"2020",
        191:"2020",
        192:"2020",
        193:"2020",
        194:"2021",
        195:"2021",
        196:"2021",
        197:"2021",
        198:"2022",
        199:"2022",
        200:"2022",
        201:"2022",
        202:"2023",
        203:"2023",
        204:"2023",
        205:"2023",
        206:"2024",
        207:"2024",
        208:"2024",
        209:"2024",
    }
    return (ciclo_to_años,)


@app.cell
def _():
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
    return (cnae_2d_to_epa,)


@app.cell
def _(ciclo_to_años, cnae_2d_to_epa, pd, xubilados_galicia):
    xubilados = pd.read_feather(xubilados_galicia).assign(
            Data=lambda x:x.CICLO.astype(int).replace(ciclo_to_años),
    Edad=lambda x:x.EDAD1.astype(int), Sector=lambda x:x.ACTA.astype('str').replace(cnae_2d_to_epa))
    return (xubilados,)


@app.cell
def _(xubilados):
    xubilados.query('Sector=="24_25"').Factor.sum().round()
    return


@app.cell
def _(xubilados):
    xubilados.query('Sector=="24_25"').groupby(['EDAD1']).Factor.sum().round()
    return


@app.cell
def _():
    (614+355)/2142
    return


@app.cell
def _(xubilados):
    xubilados.query('Sector=="24_25"&Edad>60').groupby('Data').Factor.sum().round()
    return


@app.cell
def _(xubilados):
    xubilados.query('Sector=="24_25"&Edad>60').Factor.sum().round()
    return


@app.cell
def _(xubilados):
    xubilados.query('Sector=="24_25"').groupby(['OCUPA']).Factor.sum().round()
    return


@app.cell
def _():
    793/2142
    return


@app.cell
def _(ciclo_to_años, cnae_2d_to_epa, epa_g_2d, pd):
    epa_2d = pd.read_feather(epa_g_2d).assign(
            Data=lambda x:x.CICLO.astype(int).replace(ciclo_to_años),
        Edad=lambda x:x.EDAD1.astype(int),Sector=lambda x:x.ACT.astype('str').replace(cnae_2d_to_epa))
    return (epa_2d,)


@app.cell
def _(epa_2d):
    epa_2d.query('Sector=="24_25"&Edad>60').groupby('Data').Factor.sum().div(4).round()
    return


@app.cell
def _(epa_2d):
    epa_2d.query('Sector=="24_25"&Edad>60').Factor.sum().round()/4
    return


@app.cell
def _():
    2142/5375
    return


@app.cell
def _(epa_2d):
    epa_2d.query('Sector=="24_25"&Data=="2024"&Edad>56&Edad<64').Factor.sum().round()/4
    return


@app.cell
def _(epa_2d):
    epa_2d.query('Sector=="24_25"&Data=="2024"&Edad>58&Edad<64').groupby(['OCUP']).Factor.sum().round()
    return


@app.cell
def _():
    3776*.4
    return


@app.cell
def _(epa_2d):
    epa_2d.query('Sector=="24_25"&OCUP=="73"').groupby('Data').Factor.sum().div(4).round()
    return


@app.cell
def _():
    754/3776
    return


@app.cell
def _(epa_2d):
    epa_2d.query('Sector=="24_25"&OCUP=="73"&Edad>56&Edad<64').groupby('Data').Factor.sum().div(4).round()
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ### Sector Educación
    Entre 2019 y 2024 xubiláronse 10.900 traballadores, dos que o 80% eran profesores, e o 41% xubilouse antes dos 62 anos. Estes traballadores foron reemprazados, de xeito que neste período o número de profesores empregados aumentou en 6.000.

    A previsión é que de aquí a 2030 se xubilen outros 10.300 traballadores, dos que o 70% serán profesores. Polo tanto, será necesario reemprazar a 7.250 profesores.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ### Sector Actividades Sanitarias
    Entre 2019 y 2024 xubiláronse 11.300 traballadores, dos que o 49% eran profesionais da saúde e outro 25% eran coidadores, e o 61% xubilouse entre os 65 e 66 anos. Os profesionais da saúde non foron reemprazados por completo (o número de traballadores reduciuse en 1.000 durante o periodo), pero sí os coidadores, dos que o número aumentou en 3.500.

    A previsión é que de aquí a 2030 se xubilen outros 12.500 traballadores, dos que o 32% serán profesionais da saúde e outro 25% serán coidadores. Polo tanto, será necesario reemprazar a 3.850 profesionais da saúde e 3.100 coidadores.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ### Sector Metalurxia e Produtos Metálicos
    Entre 2019 y 2024 xubiláronse 2.150 traballadores, dos que o 37% eran soldadores, e o 45% xubilouse antes dos 65 anos. Estes traballadores foron reemprazados, de xeito que neste período o número de soldadores empregados aumentou en 1.300.

    A previsión é que de aquí a 2030 se xubilen outros 1.500 traballadores, dos que o 20% serán soldadores. Polo tanto, será necesario reemprazar a 300 soldadores.
    """
    )
    return


if __name__ == "__main__":
    app.run()
