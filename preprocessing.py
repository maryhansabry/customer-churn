"""
preprocessing.py — mirrors the notebook pipeline exactly.

Notebook steps (in order):
  1. Fill missing values  (median for numeric, mode for categorical)
  2. Clip outliers        (IQR method)
  3. Fix inconsistent cat values  (Phone→Mobile Phone, COD→Cash on Delivery, etc.)
  4. Feature engineering  (OrdersPerTenure)
  5. get_dummies(drop_first=True) on the full dataframe
  6. Reindex to common_features (the 7 selected features)

Selected features (common_features from notebook):
  ['OrdersPerTenure', 'DaySinceLastOrder', 'Tenure',
   'PreferedOrderCat_Laptop & Accessory', 'MaritalStatus_Married',
   'PreferedOrderCat_Mobile', 'Complain']
"""

import numpy as np
import pandas as pd

# ── Exact feature order the model was trained on ──────────────────────────────
FEATURE_ORDER = [
    "OrdersPerTenure",
    "DaySinceLastOrder",
    "Tenure",
    "PreferedOrderCat_Laptop & Accessory",
    "MaritalStatus_Married",
    "PreferedOrderCat_Mobile",
    "Complain",
]

# ── Column name aliases (CSV uploads may use different names) ─────────────────
COLUMN_ALIASES = {
    "Tenure_Months":         "Tenure",
    "City_Tier":             "CityTier",
    "Hours_On_App_Per_Day":  "HourSpendOnApp",
    "Devices_Registered":    "NumberOfDeviceRegistered",
    "Complained":            "Complain",
    "Order_Count":           "OrderCount",
    "Days_Since_Last_Order": "DaySinceLastOrder",
    "PreferredOrderCat":     "PreferedOrderCat",
}

# ── Numeric columns (for missing-value + outlier handling) ────────────────────
NUM_COLS = [
    "Tenure", "WarehouseToHome", "HourSpendOnApp",
    "OrderAmountHikeFromlastYear", "CouponUsed",
    "OrderCount", "DaySinceLastOrder", "CashbackAmount",
    "NumberOfDeviceRegistered", "SatisfactionScore",
]


def _fix_inconsistent_values(df: pd.DataFrame) -> pd.DataFrame:
    """Replicate the notebook's replace() calls."""
    if "PreferredLoginDevice" in df.columns:
        df["PreferredLoginDevice"] = df["PreferredLoginDevice"].replace(
            {"Phone": "Mobile Phone"}
        )
    if "PreferredPaymentMode" in df.columns:
        df["PreferredPaymentMode"] = df["PreferredPaymentMode"].replace(
            {"COD": "Cash on Delivery", "CC": "Credit Card"}
        )
    if "PreferedOrderCat" in df.columns:
        df["PreferedOrderCat"] = df["PreferedOrderCat"].replace(
            {"Mobile Phone": "Mobile"}
        )
    return df


def _fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values: median for numeric, mode for categorical."""
    for col in df.columns:
        if df[col].isnull().sum() == 0:
            continue
        if df[col].dtype in ["int64", "float64"]:
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna(df[col].mode()[0])
    return df


def _clip_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """IQR-based outlier clipping on numeric columns (same as notebook)."""
    num_cols = [c for c in NUM_COLS if c in df.columns]
    for col in num_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lo = q1 - 1.5 * iqr
        hi = q3 + 1.5 * iqr
        df[col] = np.clip(df[col], lo, hi)
    return df


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full preprocessing pipeline — mirrors the notebook steps.

    Parameters
    ----------
    df : raw DataFrame uploaded by the user (CSV)

    Returns
    -------
    DataFrame with exactly FEATURE_ORDER columns, ready for model.predict_proba()
    """
    df = df.copy()

    # 1. Rename aliased columns
    df.rename(columns=COLUMN_ALIASES, inplace=True)

    # 2. Cast numeric columns
    for col in NUM_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 3. Fill missing values
    df = _fill_missing(df)

    # 4. Clip outliers
    df = _clip_outliers(df)

    # 5. Fix inconsistent categorical values
    df = _fix_inconsistent_values(df)

    # 6. Feature engineering: OrdersPerTenure
    if "OrderCount" in df.columns and "Tenure" in df.columns:
        df["OrdersPerTenure"] = df["OrderCount"] / (df["Tenure"] + 1)
    else:
        df["OrdersPerTenure"] = 0.0

    # 7. get_dummies(drop_first=True) — same as notebook
    df = pd.get_dummies(df, drop_first=True)

    # 8. Reindex to the exact 7 features, fill any missing dummies with 0
    df = df.reindex(columns=FEATURE_ORDER, fill_value=0)

    # 9. Safety: replace inf / NaN
    df = df.replace([np.inf, -np.inf], np.nan).fillna(0)

    return df


def preprocess_single(row: dict) -> np.ndarray:
    """
    Preprocess a single customer dict (from the manual input form).

    Parameters
    ----------
    row : dict — keys should include at minimum:
        Tenure, OrderCount, DaySinceLastOrder, Complain,
        PreferedOrderCat (optional), MaritalStatus (optional)

    Returns
    -------
    np.ndarray of shape (1, 7)
    """
    df = pd.DataFrame([row])
    processed = preprocess_dataframe(df)
    return processed.values  # shape (1, 7)
