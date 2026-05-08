# charts.py — All Plotly figures

import plotly.graph_objects as go
from config import C


def base_layout(title="", height=240):
    return dict(
        title=dict(text=title, font=dict(size=12, color=C["muted"]), x=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Syne, sans-serif", color=C["muted"], size=11),
        height=height,
        margin=dict(t=32, b=28, l=12, r=12),
        xaxis=dict(showgrid=False, zeroline=False, color=C["muted"],
                   tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                   zeroline=False, color=C["muted"], tickfont=dict(size=10)),
        showlegend=False,
        hoverlabel=dict(bgcolor=C["card"], bordercolor=C["border"],
                        font=dict(color=C["text"], size=11)),
    )


def gauge_chart(prob: float) -> go.Figure:
    pct   = round(prob * 100, 1)
    color = C["high"] if prob >= 0.7 else (C["medium"] if prob >= 0.4 else C["low"])

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,
        number={"suffix": "%", "font": {"size": 36, "color": color,
                                         "family": "DM Mono, monospace"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": C["muted"],
                     "tickfont": {"size": 10}},
            "bar":  {"color": color, "thickness": 0.25},
            "bgcolor": C["surface"],
            "bordercolor": "rgba(0,0,0,0)",
            "steps": [
                {"range": [0,  40], "color": "rgba(52,211,153,0.08)"},
                {"range": [40, 65], "color": "rgba(251,191,36,0.08)"},
                {"range": [65,100], "color": "rgba(248,113,113,0.08)"},
            ],
            "threshold": {"line": {"color": C["accent"], "width": 2}, "value": 40}
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Syne, sans-serif", color=C["muted"]),
        height=220,
        margin=dict(t=20, b=0, l=30, r=30),
    )
    return fig


def donut_chart(df) -> go.Figure:
    n_high   = (df["risk"] == "High").sum()
    n_medium = (df["risk"] == "Medium").sum()
    n_low    = (df["risk"] == "Low").sum()

    fig = go.Figure(go.Pie(
        labels=["High", "Medium", "Low"],
        values=[n_high, n_medium, n_low],
        hole=0.62,
        marker=dict(colors=[C["high"], C["medium"], C["low"]],
                    line=dict(color=C["bg"], width=2)),
        textinfo="none",
        hovertemplate="%{label}: %{value} customers (%{percent})<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b>{n_high}</b><br><span style='font-size:10px'>at risk</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color=C["high"], family="DM Mono, monospace"),
    )
    fig.update_layout(**base_layout("Risk distribution", height=220))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", x=1.02, y=0.5,
                    font=dict(size=11, color=C["muted"]))
    )
    return fig


def city_tier_chart(df) -> go.Figure:
    tier_df = df.groupby("CityTier")["churn_prob"].mean().reset_index()
    tier_df.columns = ["tier", "rate"]
    tier_df["rate_pct"] = (tier_df["rate"] * 100).round(1)

    fig = go.Figure(go.Bar(
        x=[f"Tier {t}" for t in tier_df["tier"]],
        y=tier_df["rate_pct"],
        marker=dict(
            color=tier_df["rate_pct"],
            colorscale=[[0, C["low"]], [0.5, C["medium"]], [1, C["high"]]],
            showscale=False,
            cornerradius=6,
        ),
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
        text=tier_df["rate_pct"].apply(lambda x: f"{x}%"),
        textposition="outside",
        textfont=dict(size=11, color=C["muted"]),
    ))
    fig.update_layout(**base_layout("Avg churn rate by city tier", height=220))
    return fig


def tenure_chart(df) -> go.Figure:
    import pandas as pd
    df = df.copy()
    df["tenure_bucket"] = pd.cut(
        df["Tenure"], bins=[-1, 3, 6, 12, 24, 999],
        labels=["0–3 mo", "3–6 mo", "6–12 mo", "12–24 mo", "24+ mo"]
    )
    ten_df = df.groupby("tenure_bucket", observed=True)["churn_prob"].mean().reset_index()
    ten_df["rate_pct"] = (ten_df["churn_prob"] * 100).round(1)

    fig = go.Figure(go.Bar(
        x=ten_df["tenure_bucket"].astype(str),
        y=ten_df["rate_pct"],
        marker=dict(
            color=ten_df["rate_pct"],
            colorscale=[[0, C["low"]], [0.5, C["medium"]], [1, C["high"]]],
            showscale=False,
            cornerradius=6,
        ),
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
        text=ten_df["rate_pct"].apply(lambda x: f"{x}%"),
        textposition="outside",
        textfont=dict(size=11, color=C["muted"]),
    ))
    fig.update_layout(**base_layout("Churn rate by tenure", height=220))
    return fig


def scatter_chart(df) -> go.Figure:
    sample = df.sample(min(300, len(df)), random_state=42)

    fig = go.Figure(go.Scatter(
        x=sample["HourSpendOnApp"],
        y=sample["churn_pct"],
        mode="markers",
        marker=dict(
            size=6,
            color=sample["churn_pct"],
            colorscale=[[0, C["low"]], [0.4, C["medium"]], [1, C["high"]]],
            opacity=0.65,
            showscale=False,
        ),
        hovertemplate="Hours: %{x:.1f}h  |  Risk: %{y:.1f}%<extra></extra>",
    ))
    fig.add_shape(
        type="line", x0=0, x1=sample["HourSpendOnApp"].max(), y0=40, y1=40,
        line=dict(color=C["accent"], width=1, dash="dot")
    )
    fig.update_layout(**base_layout("Hour spend vs churn risk", height=220))
    return fig


def histogram_chart(df) -> go.Figure:
    fig = go.Figure(go.Histogram(
        x=df["churn_pct"],
        nbinsx=25,
        marker=dict(
            color=df["churn_pct"].clip(upper=99),
            colorscale=[[0, C["low"]], [0.4, C["medium"]], [1, C["high"]]],
            showscale=False,
            line=dict(width=0),
        ),
        hovertemplate="Score %{x:.0f}%: %{y} customers<extra></extra>",
    ))
    fig.add_shape(
        type="line", x0=40, x1=40, y0=0,
        y1=df["churn_pct"].value_counts().max() * 1.1,
        line=dict(color=C["accent"], width=1.5, dash="dot")
    )
    fig.add_annotation(
        x=40, y=0, text="threshold", showarrow=False,
        yanchor="bottom", font=dict(size=10, color=C["accent"]), yshift=4
    )
    fig.update_layout(**base_layout("Risk score distribution", height=220))
    fig.update_layout(bargap=0.05)
    return fig


def complain_chart(df) -> go.Figure:
    comp_df = df.groupby("Complain")["churn_prob"].mean().reset_index()
    comp_df["label"]    = comp_df["Complain"].map({0: "No complaint", 1: "Complained"})
    comp_df["rate_pct"] = (comp_df["churn_prob"] * 100).round(1)

    fig = go.Figure(go.Bar(
        x=comp_df["label"],
        y=comp_df["rate_pct"],
        marker=dict(color=[C["low"], C["high"]], cornerradius=6),
        text=comp_df["rate_pct"].apply(lambda x: f"{x}%"),
        textposition="outside",
        textfont=dict(size=12, color=C["muted"]),
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(**base_layout("Churn rate: complaint vs no complaint", height=220))
    return fig
