import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import requests
import pandas as pd

from pathlib import Path

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# show latest date from files

data = [{
    'id': 'hospi',
    'url': 'https://www.data.gouv.fr/fr/datasets/r/63352e38-d353-4b54-bfd1-f1b3ee1cabd7',
}, {
    'id': 'hospi_nouveaux',
    'url': 'https://www.data.gouv.fr/fr/datasets/r/6fadff46-9efd-4c53-942a-54aca783c30c'
}, {
    'id': 'hospi_clage',
    'url': 'https://www.data.gouv.fr/fr/datasets/r/08c18e08-6780-452d-9b8c-ae244ad529b3'
}, {
    'id': 'hospi_etab',
    'url': 'https://www.data.gouv.fr/fr/datasets/r/41b9bd2a-b5b6-4271-8878-e45a8902ef00'
}]

# download data w/ caching
# TODO: handle cache elsewhere for dokku?
data_path = Path('./data')
data_path.mkdir(exist_ok=True)
for item in data:
    r = requests.head(item['url'])
    location = r.headers['Location']
    filename = location.split('/')[-1]
    filepath = data_path / filename
    if not filepath.exists():
        r = requests.get(location)
        with open(filepath, 'wb') as dfile:
            dfile.write(r.content)
    item['filepath'] = filepath

# hospi

datum = [d for d in data if d['id'] == 'hospi'][0]
cols = ["hosp", "rea", "rad", "dc"]
df_hospi = pd.read_csv(datum['filepath'], delimiter=";", parse_dates=["jour"])
df_hospi = df_hospi[df_hospi["sexe"] == 0].groupby(["jour"], as_index=False).agg({k: sum for k in cols})

fig_hospi = px.bar(df_hospi, x="jour", y=cols, title="Données hospitalières")

# hospi_nouveaux

datum = [d for d in data if d['id'] == 'hospi_nouveaux'][0]
cols = ["incid_hosp", "incid_rea", "incid_dc", "incid_rad"]
df_hospi_nouveaux = pd.read_csv(datum['filepath'], delimiter=";", parse_dates=["jour"])
df_hospi_nouveaux = df_hospi_nouveaux.groupby(["jour"], as_index=False).agg({k: sum for k in cols})

fig_hospi_nouveaux = px.bar(df_hospi_nouveaux, x="jour", y=cols, title="Données hospitalières nouveaux")

# hospi_clage

datum = [d for d in data if d['id'] == 'hospi_clage'][0]
cols = ["hosp", "rea", "rad", "dc"]
df_hospi_clage = pd.read_csv(datum['filepath'], delimiter=";", parse_dates=["jour"])
df_hospi_clage = df_hospi_clage.groupby(["jour", "cl_age90"], as_index=False).agg({k: sum for k in cols})
df_hospi_clage["cl_age90"] = df_hospi_clage["cl_age90"].astype(str)

figs_clage = []
for c in cols:
    fig = px.bar(df_hospi_clage, x="jour", y=[c], color="cl_age90", title=f"Données hospitalières clage {c}")
    figs_clage.append(fig)

# hospi_etab

datum = [d for d in data if d['id'] == 'hospi_etab'][0]
cols = ["nb"]
df_hospi_etab = pd.read_csv(datum['filepath'], delimiter=";", parse_dates=["jour"])
df_hospi_etab = df_hospi_etab.groupby(["jour"], as_index=False).agg({k: sum for k in cols})

fig_hospi_etab = px.bar(df_hospi_etab, x="jour", y=cols, title="Données hospitalières etab")

app.layout = html.Div(children=[
    html.H1(children='Données hospitalières SPF'),
    dcc.Graph(
        id='hospi',
        figure=fig_hospi,
    ),
    dcc.Graph(
        id='hospi_nouveaux',
        figure=fig_hospi_nouveaux,
    ),
    *[
        dcc.Graph(id=f'hospi_clage_{idx}', figure=fig) for idx, fig in enumerate(figs_clage)
    ],
    dcc.Graph(
        id='hospi_etab',
        figure=fig_hospi_etab,
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)
