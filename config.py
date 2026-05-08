# config.py — Colors, constants, feature order

THRESHOLD = 0.4

FEATURE_ORDER = [
    "Tenure", "CityTier", "HourSpendOnApp",
    "NumberOfDeviceRegistered", "Complain",
    "OrderCount", "DaySinceLastOrder"
]

C = {
    "bg":      "#080811",
    "surface": "#0f0f1c",
    "card":    "#131320",
    "border":  "rgba(255,255,255,0.07)",
    "text":    "#e2e2ee",
    "muted":   "rgba(255,255,255,0.35)",
    "accent":  "#7c6af7",
    "high":    "#f87171",
    "medium":  "#fbbf24",
    "low":     "#34d399",
    "monitor": "#94a3b8",
}

ACTION_ICONS = {
    "call":         "📞",
    "coupon":       "🎁",
    "notification": "📱",
    "monitor":      "👀",
    "safe":         "✅",
}
