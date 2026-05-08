# app.py — Entry point only

import pickle
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from config import C
from layout import topbar, single_page
from callbacks import register_callbacks

# ── Load model ────────────────────────────────────────────────────────────────
with open("xgb_churn_model.pkl", "rb") as f:
    MODEL = pickle.load(f)

# ── App ───────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;500;700&display=swap"
    ],
    suppress_callback_exceptions=True
)
app.title = "ChurnInsight"

app.layout = html.Div([
    dcc.Store(id="data-store"),
    dcc.Store(id="single-store"),
    dcc.Store(id="chat-history", data=[]),
    topbar(),
    html.Div(id="page-content"),
], style={
    "background": C["bg"],
    "minHeight": "100vh",
    "fontFamily": "Syne, sans-serif",
    "color": C["text"],
})

# ── Register callbacks ────────────────────────────────────────────────────────
register_callbacks(app, MODEL)
server = app.server
# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=False)
    # print("🚀  ChurnInsight → http://localhost:8050")
    # app.run(debug=True, port=8050)
