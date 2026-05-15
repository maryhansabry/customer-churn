# layout.py — All UI components and page builders

from dash import dcc, html, dash_table
import plotly.graph_objects as go
from config import C, ACTION_ICONS
from charts import (
    gauge_chart, donut_chart, city_tier_chart,
    tenure_chart, scatter_chart, histogram_chart, complain_chart
)


# ── Reusable components ───────────────────────────────────────────────────────

def kpi_card(label, value, sub="", color=C["accent"]):
    return html.Div([
        html.Div(style={
            "height": "3px", "background": color,
            "borderRadius": "4px 4px 0 0", "marginBottom": "14px"
        }),
        html.Div(label, style={"fontSize": "11px", "color": C["muted"],
                                "marginBottom": "6px", "letterSpacing": ".5px"}),
        html.Div(value, style={
            "fontSize": "26px", "fontWeight": "700", "color": color,
            "fontFamily": "DM Mono, monospace", "lineHeight": "1"
        }),
        html.Div(sub, style={"fontSize": "11px", "color": C["muted"],
                              "marginTop": "5px"}),
    ], style={
        "background": C["card"], "border": f"0.5px solid {C['border']}",
        "borderRadius": "12px", "padding": "16px", "transition": "border-color .2s",
    })


def chart_card(children, style=None):
    s = {
        "background": C["card"], "border": f"0.5px solid {C['border']}",
        "borderRadius": "12px", "padding": "16px", "height": "100%",
    }
    if style:
        s.update(style)
    return html.Div(children, style=s)


def action_pill(label, count, color):
    return html.Div([
        html.Span(label, style={"fontSize": "12px", "color": color, "fontWeight": "500"}),
        html.Span(str(count), style={
            "marginLeft": "8px", "fontSize": "13px",
            "fontFamily": "DM Mono, monospace", "color": C["text"],
        }),
    ], style={
        "background": f"{color}12", "border": f"0.5px solid {color}44",
        "borderRadius": "8px", "padding": "8px 14px",
        "display": "flex", "alignItems": "center",
    })


# ── Top bar ───────────────────────────────────────────────────────────────────

def topbar():
    return html.Div([
        html.Span("Churn", style={"color": C["text"], "fontWeight": "700"}),
        html.Span("Insight", style={"color": C["accent"], "fontWeight": "700"}),
        html.Div([
            html.Button("Single Customer", id="tab-single", className="tab-btn active-tab"),
            html.Button("Batch Analysis",  id="tab-batch",  className="tab-btn"),
        ], style={
            "marginLeft": "auto", "display": "flex", "gap": "4px",
            "background": "rgba(255,255,255,0.04)",
            "borderRadius": "8px", "padding": "3px",
        }),
    ], style={
        "background": "#0d0d1a", "borderBottom": f"0.5px solid {C['border']}",
        "padding": "12px 28px", "display": "flex", "alignItems": "center", "gap": "2px",
        "fontSize": "17px", "letterSpacing": "-0.5px", "fontFamily": "Syne, sans-serif",
    })


# ── Single customer page ──────────────────────────────────────────────────────

def single_page():
    inp_style = {
        "width": "100%", "background": "rgba(255,255,255,0.05)",
        "border": f"0.5px solid {C['border']}", "borderRadius": "8px",
        "padding": "8px 12px", "color": C["text"], "fontSize": "13px",
        "fontFamily": "DM Mono, monospace",
    }

    def field(label, el):
        return html.Div([
            html.Label(label, style={
                "fontSize": "11px", "color": C["muted"],
                "marginBottom": "5px", "display": "block", "letterSpacing": ".4px"
            }),
            el,
        ], style={"marginBottom": "14px"})

    return html.Div([
        html.Div([
            # Form
            html.Div([
                html.Div("Customer Details", style={
                    "fontSize": "13px", "fontWeight": "500",
                    "color": C["muted"], "marginBottom": "18px", "letterSpacing": ".5px"
                }),
                field("Tenure (months)", dcc.Input(
                    id="s-tenure", type="number", value=12, min=0, style=inp_style)),
                field("City Tier", dcc.Dropdown(
                    id="s-citytier",
                    options=[
                        {"label": "Tier 1 — Major city",    "value": 1},
                        {"label": "Tier 2 — Mid-size city", "value": 2},
                        {"label": "Tier 3 — Small city",    "value": 3},
                    ],
                    value=1, style={**inp_style, "cursor": "pointer"},
                    className="dark-dropdown"
                )),
                field("Hours on App / day", dcc.Input(
                    id="s-hour", type="number", value=3.0, min=0, step=0.5, style=inp_style)),
                field("Devices Registered", dcc.Input(
                    id="s-devices", type="number", value=2, min=0, style=inp_style)),
                field("Complained?", dcc.Dropdown(
                    id="s-complain",
                    options=[{"label": "No", "value": 0}, {"label": "Yes", "value": 1}],
                    value=0, style={**inp_style, "cursor": "pointer"},
                    className="dark-dropdown"
                )),
                field("Order Count", dcc.Input(
                    id="s-orders", type="number", value=5, min=0, style=inp_style)),
                field("Days Since Last Order", dcc.Input(
                    id="s-days", type="number", value=7, min=0, style=inp_style)),

                html.Button("Predict →", id="predict-btn", style={
                    "width": "100%",
                    "background": f"linear-gradient(135deg, {C['accent']}, #5b4fcf)",
                    "border": "none", "borderRadius": "10px", "color": "#fff",
                    "padding": "11px", "fontSize": "14px", "fontWeight": "600",
                    "cursor": "pointer", "marginTop": "4px",
                    "fontFamily": "Syne, sans-serif",
                }),
            ], style={
                "background": C["card"], "border": f"0.5px solid {C['border']}",
                "borderRadius": "14px", "padding": "22px",
                "width": "290px", "flexShrink": "0",
            }),

            # Result panel
            html.Div(id="single-result", style={"flex": "1"}),

        ], style={
            "display": "flex", "gap": "20px",
            "padding": "24px 28px", "alignItems": "flex-start",
        }),
    ])


def build_single_result(prob: float, rec: dict):
    pct   = round(prob * 100, 1)
    color = C["high"] if prob >= 0.7 else (C["medium"] if prob >= 0.4 else C["low"])
    label = "High Risk" if prob >= 0.7 else ("Medium Risk" if prob >= 0.4 else "Low Risk")
    icon  = ACTION_ICONS.get(rec["action"], "•")

    return html.Div([
        # Label
        html.Div([
            html.Div(label, style={"fontSize": "22px", "fontWeight": "700",
                                   "color": color, "marginBottom": "4px"}),
            html.Div(f"Churn probability: {pct}%",
                     style={"fontSize": "13px", "color": C["muted"]}),
        ], style={"marginBottom": "16px"}),

        # Gauge
        chart_card(
            [dcc.Graph(figure=gauge_chart(prob), config={"displayModeBar": False})],
            style={"marginBottom": "14px", "padding": "8px"}
        ),

        # Recommendation
        html.Div([
            html.Div([
                html.Span(icon, style={"fontSize": "20px", "marginRight": "10px"}),
                html.Span(rec["action_label"], style={
                    "fontSize": "15px", "fontWeight": "600",
                    "color": rec["action_color"],
                }),
                html.Span(
                    "Actionable" if rec["actionable"] else "Monitor only",
                    style={
                        "marginLeft": "auto", "fontSize": "11px",
                        "padding": "2px 10px", "borderRadius": "10px",
                        "background": "rgba(52,211,153,0.1)" if rec["actionable"]
                                      else "rgba(148,163,184,0.1)",
                        "color": C["low"] if rec["actionable"] else C["monitor"],
                    }
                ),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
            html.P(rec["reason"], style={
                "fontSize": "13px", "color": C["muted"],
                "lineHeight": "1.6", "margin": "0",
            }),
        ], style={
            "background": C["card"],
            "border": f"1px solid {rec['action_color']}33",
            "borderRadius": "12px", "padding": "16px", "marginBottom": "14px",
        }),

        # Chat
        html.Div([
            html.Div("Ask the AI about this customer", style={
                "fontSize": "12px", "color": C["muted"],
                "marginBottom": "10px", "fontWeight": "500",
            }),
            html.Div(id="single-chat-msgs", style={
                "display": "flex", "flexDirection": "column",
                "gap": "8px", "marginBottom": "10px",
                "maxHeight": "200px", "overflowY": "auto",
            }),
            html.Div([
                dcc.Input(
                    id="single-chat-input",
                    placeholder="e.g. Why is this customer at risk?",
                    style={
                        "flex": "1", "background": "rgba(255,255,255,0.05)",
                        "border": f"0.5px solid {C['border']}",
                        "borderRadius": "20px", "padding": "8px 14px",
                        "color": C["text"], "fontSize": "12px",
                        "fontFamily": "Syne, sans-serif",
                    },
                    debounce=False, n_submit=0,
                ),
                html.Button("↑", id="single-chat-send", style={
                    "width": "32px", "height": "32px", "flexShrink": "0",
                    "background": "rgba(124,106,247,0.2)",
                    "border": f"0.5px solid {C['accent']}55",
                    "borderRadius": "50%", "color": C["accent"],
                    "cursor": "pointer", "fontSize": "14px",
                }),
            ], style={"display": "flex", "gap": "8px", "alignItems": "center"}),
        ], style={
            "background": C["card"], "border": f"0.5px solid {C['border']}",
            "borderRadius": "12px", "padding": "16px",
        }),
    ])


# ── Batch page ────────────────────────────────────────────────────────────────

def batch_page():
    return html.Div([
        html.Div([
            dcc.Upload(
                id="upload-data",
                children=html.Button("Upload CSV", style={
                    "background": "rgba(124,106,247,0.15)",
                    "border": f"0.5px solid {C['accent']}55",
                    "color": C["accent"], "borderRadius": "8px",
                    "padding": "6px 18px", "fontSize": "12px",
                    "cursor": "pointer", "fontFamily": "Syne, sans-serif",
                }),
            ),
            html.Div(id="upload-status", style={"fontSize": "12px", "color": C["muted"]}),
        ], style={
            "background": "#0f0f1e", "borderBottom": f"0.5px solid {C['border']}",
            "padding": "10px 28px", "display": "flex", "alignItems": "center", "gap": "14px",
        }),
        html.Div(id="batch-content", style={"padding": "24px 28px"}),
    ])


def build_batch_dashboard(df):
    total            = len(df)
    n_high           = int((df["risk"] == "High").sum())
    churn_pct        = round(n_high / total * 100, 1)
    avg_prob         = round(df["churn_prob"].mean() * 100, 1)
    actionable_count = int(df["actionable"].sum())
    action_counts    = df[df["risk"] == "High"]["action"].value_counts()

    # Table
    disp = df.copy()
    disp["churn_pct"] = disp["churn_pct"].apply(lambda x: f"{x}%")

    table = dash_table.DataTable(
        data=disp.to_dict("records"),
        columns=[
            {"name": "Tenure (mo)",       "id": "Tenure"},
            {"name": "City Tier",         "id": "CityTier"},
            {"name": "Hours/day",         "id": "HourSpendOnApp"},
            {"name": "Complain",          "id": "Complain"},
            {"name": "Last Order (days)", "id": "DaySinceLastOrder"},
            {"name": "Churn %",           "id": "churn_pct"},
            {"name": "Risk",              "id": "risk"},
            {"name": "Action",            "id": "action"},
            {"name": "Why",               "id": "reason"},
        ],
        page_size=10,
        sort_action="native",
        filter_action="native",
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": C["surface"], "color": C["muted"],
            "fontSize": "11px", "fontWeight": "400",
            "border": f"0.5px solid {C['border']}",
            "fontFamily": "Syne, sans-serif", "padding": "8px 12px",
        },
        style_cell={
            "backgroundColor": C["card"], "color": "rgba(255,255,255,0.55)",
            "fontSize": "12px", "border": f"0.5px solid rgba(255,255,255,0.04)",
            "fontFamily": "Syne, sans-serif", "padding": "8px 12px",
            "maxWidth": "200px", "overflow": "hidden", "textOverflow": "ellipsis",
        },
        style_data_conditional=[
            {"if": {"filter_query": '{risk} = "High"',   "column_id": "risk"},
             "color": C["high"], "fontWeight": "600"},
            {"if": {"filter_query": '{risk} = "Medium"', "column_id": "risk"},
             "color": C["medium"], "fontWeight": "600"},
            {"if": {"filter_query": '{risk} = "Low"',    "column_id": "risk"},
             "color": C["low"]},
        ],
    )

    return html.Div([
        # KPIs
        html.Div([
            kpi_card("Total Customers",  f"{total:,}",           "from CSV",    C["accent"]),
            kpi_card("At Risk (High)",   f"{n_high:,}",          "prob > 40%",  C["high"]),
            kpi_card("Churn Rate",       f"{churn_pct}%",        "high risk",   C["medium"]),
            kpi_card("Avg Risk Score",   f"{avg_prob}%",         "all customers", C["low"]),
            kpi_card("Actionable Cases", f"{actionable_count:,}","need action", C["accent"]),
        ], style={
            "display": "grid", "gridTemplateColumns": "repeat(5, 1fr)",
            "gap": "10px", "marginBottom": "16px",
        }),

        # Action summary
        html.Div([
            html.Div("Recommended actions for high-risk customers:", style={
                "fontSize": "12px", "color": C["muted"],
                "marginRight": "14px", "whiteSpace": "nowrap",
            }),
            *[action_pill(
                act, cnt,
                C["high"] if "Call" in act else C["medium"] if "Coupon" in act else C["monitor"]
              ) for act, cnt in action_counts.items()],
        ], style={
            "display": "flex", "alignItems": "center", "gap": "10px",
            "background": C["card"], "border": f"0.5px solid {C['border']}",
            "borderRadius": "10px", "padding": "10px 16px",
            "marginBottom": "16px", "flexWrap": "wrap",
        }),

        # Charts row 1
        html.Div([
            chart_card([dcc.Graph(figure=donut_chart(df),    config={"displayModeBar": False})]),
            chart_card([dcc.Graph(figure=city_tier_chart(df),config={"displayModeBar": False})]),
            chart_card([dcc.Graph(figure=complain_chart(df), config={"displayModeBar": False})]),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr",
                  "gap": "12px", "marginBottom": "12px"}),

        # Charts row 2
        html.Div([
            chart_card([dcc.Graph(figure=tenure_chart(df),   config={"displayModeBar": False})]),
            chart_card([dcc.Graph(figure=scatter_chart(df),  config={"displayModeBar": False})]),
            chart_card([dcc.Graph(figure=histogram_chart(df),config={"displayModeBar": False})]),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr",
                  "gap": "12px", "marginBottom": "16px"}),

        # Table
        html.Div([
            html.Div([
                html.Span("Top at-risk customers", style={
                    "fontSize": "13px", "color": C["muted"], "fontWeight": "500"
                }),
                html.Button("Download CSV", id="download-btn", style={
                    "marginLeft": "auto", "fontSize": "11px", "color": C["accent"],
                    "background": "rgba(124,106,247,0.1)",
                    "border": f"0.5px solid {C['accent']}44",
                    "borderRadius": "6px", "padding": "4px 14px",
                    "cursor": "pointer", "fontFamily": "Syne, sans-serif",
                }),
                dcc.Download(id="download-csv"),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "12px"}),
            table,
        ], style={
            "background": C["card"], "border": f"0.5px solid {C['border']}",
            "borderRadius": "12px", "padding": "16px",
        }),
    ])
