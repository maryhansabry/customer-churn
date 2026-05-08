# callbacks.py — All Dash callbacks

import base64
import io
import os

import dash
import numpy as np
import pandas as pd
import google.generativeai as genai
from dash import Input, Output, State, html, dcc, callback_context
from dotenv import load_dotenv

from config import C, FEATURE_ORDER, THRESHOLD
from layout import build_single_result, build_batch_dashboard
from recommendations import get_recommendation, build_chat_context

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
GEMINI = genai.GenerativeModel("gemini-2.5-flash")


# ── Column normalization ──────────────────────────────────────────────────────
# Map many possible user column names → the model's expected feature names.
COLUMN_ALIASES = {
    "Tenure": [
        "tenure", "tenure_months", "tenuremonths", "tenure_month",
        "months_tenure", "customer_tenure",
    ],
    "CityTier": [
        "citytier", "city_tier", "city tier", "tier",
    ],
    "HourSpendOnApp": [
        "hourspendonapp", "hours_on_app_per_day", "hours_on_app",
        "hours_app", "hour_spend_on_app", "app_hours", "hoursonapp",
    ],
    "NumberOfDeviceRegistered": [
        "numberofdeviceregistered", "devices_registered", "device_registered",
        "num_devices", "devices", "number_of_devices",
    ],
    "Complain": [
        "complain", "complained", "complaint", "has_complained", "complaints",
    ],
    "OrderCount": [
        "ordercount", "order_count", "orders", "num_orders", "total_orders",
    ],
    "DaySinceLastOrder": [
        "daysincelastorder", "days_since_last_order", "days_last_order",
        "last_order_days", "days_since_order",
    ],
}


def _norm(s: str) -> str:
    return "".join(ch for ch in str(s).lower() if ch.isalnum() or ch == "_")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename incoming columns to the model's expected feature names and
    coerce common text values (Tier 1, Yes/No) into numerics."""
    df = df.copy()

    # Build {normalized_user_col: original_col}
    norm_map = {_norm(c): c for c in df.columns}

    rename = {}
    for target, aliases in COLUMN_ALIASES.items():
        # exact target also accepted
        candidates = [_norm(target)] + [_norm(a) for a in aliases]
        for cand in candidates:
            if cand in norm_map and norm_map[cand] != target:
                rename[norm_map[cand]] = target
                break
    if rename:
        df = df.rename(columns=rename)

    # CityTier: "Tier 1" → 1
    if "CityTier" in df.columns:
        df["CityTier"] = (
            df["CityTier"].astype(str)
            .str.extract(r"(\d+)", expand=False)
            .fillna(df["CityTier"])
        )
        df["CityTier"] = pd.to_numeric(df["CityTier"], errors="coerce").fillna(1).astype(int)

    # Complain: Yes/No/True/False → 1/0
    if "Complain" in df.columns:
        def _yn(v):
            s = str(v).strip().lower()
            if s in ("yes", "y", "true", "1"): return 1
            if s in ("no", "n", "false", "0", "nan", ""): return 0
            try: return int(float(s) > 0)
            except: return 0
        df["Complain"] = df["Complain"].map(_yn)

    # Coerce remaining numeric features
    for col in ["Tenure", "HourSpendOnApp", "NumberOfDeviceRegistered",
                "OrderCount", "DaySinceLastOrder"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def predict_df(df: pd.DataFrame, model) -> pd.DataFrame:
    df = normalize_columns(df)
    for col in FEATURE_ORDER:
        if col not in df.columns:
            df[col] = 0
    X = df[FEATURE_ORDER].fillna(0).values
    probs = model.predict_proba(X)[:, 1]
    df["churn_prob"] = probs
    df["churn_pct"]  = (probs * 100).round(1)
    df["risk"] = pd.cut(
        probs, bins=[-1, 0.4, 0.65, 1.0],
        labels=["Low", "Medium", "High"]
    )
    recs = [get_recommendation(row, p) for row, p in
            zip(df.to_dict("records"), probs)]
    df["action"]       = [r["action_label"] for r in recs]
    df["action_color"] = [r["action_color"]  for r in recs]
    df["reason"]       = [r["reason"]        for r in recs]
    df["actionable"]   = [r["actionable"]    for r in recs]
    return df


def register_callbacks(app, model):

    # ── Tab switching ─────────────────────────────────────────────────────
    @app.callback(
        Output("page-content", "children"),
        Input("tab-single", "n_clicks"),
        Input("tab-batch",  "n_clicks"),
        prevent_initial_call=False,
    )
    def switch_tab(n1, n2):
        from layout import single_page, batch_page
        ctx = callback_context
        if not ctx.triggered or ctx.triggered[0]["prop_id"] == ".":
            return single_page()
        btn = ctx.triggered[0]["prop_id"].split(".")[0]
        return batch_page() if btn == "tab-batch" else single_page()

    # ── Single prediction ─────────────────────────────────────────────────
    @app.callback(
        Output("single-result", "children"),
        Output("single-store",  "data"),
        Input("predict-btn",    "n_clicks"),
        State("s-tenure",   "value"),
        State("s-citytier", "value"),
        State("s-hour",     "value"),
        State("s-devices",  "value"),
        State("s-complain", "value"),
        State("s-orders",   "value"),
        State("s-days",     "value"),
        prevent_initial_call=True,
    )
    def predict_single(n, tenure, city, hour, devices, complain, orders, days):
        row = {
            "Tenure":                   tenure   or 0,
            "CityTier":                 city     or 1,
            "HourSpendOnApp":           hour     or 0,
            "NumberOfDeviceRegistered": devices  or 0,
            "Complain":                 complain or 0,
            "OrderCount":               orders   or 0,
            "DaySinceLastOrder":        days     or 0,
        }
        X    = np.array([[row[f] for f in FEATURE_ORDER]])
        prob = float(model.predict_proba(X)[0][1])
        rec  = get_recommendation(row, prob)
        ctx  = build_chat_context(row, prob, rec)
        return build_single_result(prob, rec), {"context": ctx, "history": []}

    # ── Single chat ───────────────────────────────────────────────────────
    @app.callback(
        Output("single-chat-msgs",  "children"),
        Output("single-store",      "data", allow_duplicate=True),
        Output("single-chat-input", "value"),
        Input("single-chat-send",   "n_clicks"),
        Input("single-chat-input",  "n_submit"),
        State("single-chat-input",  "value"),
        State("single-store",       "data"),
        prevent_initial_call=True,
    )
    def single_chat(n_click, n_sub, user_msg, store):
        if not user_msg or not store:
            return dash.no_update, dash.no_update, dash.no_update

        history = store.get("history", [])
        context = store.get("context", "")

        history.append({"role": "user", "content": user_msg})

        # Build prompt with last 6 messages
        prompt = f"""You are a concise customer retention analyst.
Answer in 2-3 sentences max. Be direct and actionable.

Context:
{context}

Conversation:
"""
        for m in history[-6:]:
            role = "User" if m["role"] == "user" else "Assistant"
            prompt += f"{role}: {m['content']}\n"

        try:
            response = GEMINI.generate_content(prompt)
            answer   = response.text.strip() if response.text else "No response."
        except Exception as e:
            answer = f"Error: {str(e)}"

        history.append({"role": "assistant", "content": answer})

        msg_els = [
            html.Div(m["content"], style={
                "fontSize": "12px", "padding": "8px 12px",
                "borderRadius": "10px", "lineHeight": "1.6",
                "maxWidth": "90%",
                "alignSelf": "flex-end"  if m["role"] == "user" else "flex-start",
                "background":  "rgba(124,106,247,0.18)" if m["role"] == "user"
                               else "rgba(255,255,255,0.06)",
                "color":       "#c4baff" if m["role"] == "user"
                               else "rgba(255,255,255,0.6)",
                "borderBottomRightRadius": "3px"  if m["role"] == "user" else "10px",
                "borderBottomLeftRadius":  "10px" if m["role"] == "user" else "3px",
            }) for m in history
        ]

        store["history"] = history
        return msg_els, store, ""

    # ── Batch upload ──────────────────────────────────────────────────────
    @app.callback(
        Output("upload-status", "children"),
        Output("data-store",    "data"),
        Output("batch-content", "children"),
        Input("upload-data",    "contents"),
        State("upload-data",    "filename"),
        prevent_initial_call=True,
    )
    def process_upload(contents, filename):
        if contents is None:
            return "No file", None, ""
        _, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        df = predict_df(df, model)

        status = html.Span([
            html.Span(filename, style={
                "background": "rgba(52,211,153,0.1)",
                "border": "0.5px solid rgba(52,211,153,0.25)",
                "color": C["low"], "borderRadius": "6px",
                "padding": "2px 10px", "fontSize": "11px", "marginRight": "8px",
            }),
            html.Span(f"{len(df):,} customers loaded",
                      style={"fontSize": "12px", "color": C["muted"]}),
        ])
        return status, df.to_json(), build_batch_dashboard(df)

    # ── Download CSV ──────────────────────────────────────────────────────
    @app.callback(
        Output("download-csv", "data"),
        Input("download-btn",  "n_clicks"),
        State("data-store",    "data"),
        prevent_initial_call=True,
    )
    def download(n, json_data):
        if not json_data:
            return dash.no_update
        df = pd.read_json(json_data)
        return dcc.send_data_frame(df.to_csv, "churn_predictions.csv", index=False)
