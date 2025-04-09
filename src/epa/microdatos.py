import pyreadr
import itertools
import pandas as pd
import numpy as np


def microdatos(datafile_url: str) -> pd.DataFrame:
    """
    Extrae los microdatos a partir del archivo de R a un dataframe de pandas

    Parameters
    ----------
    datafile_url : str
    Senda donde está localizado el archivo en formato R

    Returns
    -------
    microdatos : pd.DataFrame
    Dataframe de pandas con los microdatos
    """
    return pyreadr.read_r(datafile_url)['Microdatos']

def diseño(design_url: str) -> dict:
    """
    Extrae la información contenida en el diccionario a partir del archivo de Excel a un dict 

    Parameters
    ----------
    design_url : str
    Senda donde está localizado el archivo de diccionario

    Returns
    -------
    diseño : dict
    Diccionario con los dataframes de pandas correspondientes a cada hoja del archivo de Excel
    """
    return pd.read_excel(design_url, sheet_name=None)

def diseño_dataframe(design_url: str) -> pd.DataFrame:
    """
    Construye el dataframe con los metadatos a partir del dict anterior

    Parameters
    ----------
    design_url : str
    Senda donde está localizado el archivo de diccionario

    Returns
    -------
    diseño_df : pd.DataFrame
    Dataframe de pandas con los metadatos ampliados
    """
    return (
            diseño(design_url)[list(diseño(design_url).keys())[0]]
            .T.reset_index(drop=True)
            .set_index(0)
            .drop(np.nan)
            .T.iloc[:-9, :]
        )

def diccionario_df(design_url: str) -> pd.DataFrame:
    """
    Construye el dataframe con el diccionario a partir del dict

    Parameters
    ----------
    design_url : str
    Senda donde está localizado el archivo de diccionario

    Returns
    -------
    diccionario_df : pd.DataFrame
    Dataframe de pandas con el diccionario
    """
    df = pd.concat([diseño(design_url).get(key) for key in
                      [i for i in diseño(design_url).keys() if "Tablas" in i]]).reset_index(
        drop=True
    )
    cuts = [
        index for index, row in df.drop(0).iterrows() if row.isna().all()
    ] + [df.shape[0]]
    df_cut = [df.iloc[cuts[i] : cuts[i + 1]] for i in range(len(cuts) - 1) if cuts[i + 1] - cuts[i] >1]
    keys = list(
        itertools.chain(
            *[
                df.query(
                    '`Unnamed: 1`!="Descripción"&`Unnamed: 0`.notnull()&`Unnamed: 1`.isnull()'
                ).iloc[:, 0]
                for df in df_cut
            ]
        )
    )
    values = [
        df.query(
            '`Unnamed: 1`!="Descripción"&`Unnamed: 0`.notnull()&`Unnamed: 1`.notnull()'
        )
        .iloc[:, :-1]
        .set_index("Unnamed: 0")
        .to_dict()["Unnamed: 1"]
        for df in df_cut
    ]
    return (
        pd.Series(dict(zip(keys, values)))
        .reset_index()
        .rename(
            columns={"index": "Diccionario de la variable", 0: "Diccionario"}
        )
    )

def diccionario(design_url: str) -> pd.DataFrame:
    """
    Construye el dataframe con los metadatos y el diccionario

    Parameters
    ----------
    design_url : str
    Senda donde está localizado el archivo de diccionario

    Returns
    -------
    diccionario : pd.DataFrame
    Dataframe de pandas con los metadatos y el diccionario
    """
    return diseño_dataframe(design_url).merge(
    diccionario_df(design_url), how="left"
    )
