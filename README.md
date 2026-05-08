# ChurnInsight Dashboard
https://customer-churn-production-4ac0.up.railway.app/ 
Customer churn prediction dashboard powered by XGBoost + Claude AI.

## Project Structure

```
churn_dashboard/
├── app.py                  ← Main Dash app
├── recommendations.py      ← Actionable insights engine
├── xgb_churn_model.pkl     ← Your trained model (copy here)
├── requirements.txt        ← Dependencies
├── assets/
│   └── style.css           ← Dark theme CSS
└── README.md
```

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your model
Copy `xgb_churn_model.pkl` into the `churn_dashboard/` folder.

### 3. Add your Anthropic API key
```bash
# Mac/Linux
export ANTHROPIC_API_KEY=sk-ant-...

# Windows
set ANTHROPIC_API_KEY=sk-ant-...
```

> Get your key from: https://console.anthropic.com

### 4. Run the app
```bash
python app.py
```

Open → http://localhost:8050

---

## Features

### Single Customer Tab
- Enter 7 customer inputs
- Get churn probability + gauge chart
- See recommended action (call / coupon / notification / monitor)
- Chat with AI about the specific customer

### Batch Analysis Tab
- Upload any CSV with customer data
- Automatic predictions for all customers
- 6 interactive charts:
  - Risk distribution (donut)
  - Churn by city tier (bar)
  - Churn vs complaint (comparison)
  - Churn by tenure (trend)
  - Hour spend vs risk (scatter)
  - Risk score distribution (histogram)
- Action summary: how many need calls vs coupons vs notifications
- Sortable/filterable table with reasons
- Download results as CSV

---

## CSV Format

Your CSV needs these columns (flexible naming):

| Column | Example |
|--------|---------|
| Tenure | 12 |
| CityTier | 1 |
| HourSpendOnApp | 3.5 |
| NumberOfDeviceRegistered | 2 |
| Complain | 0 |
| OrderCount | 5 |
| DaySinceLastOrder | 7 |

---

## Recommendation Logic

| Trigger | Action |
|---------|--------|
| Complained = Yes | 📞 Retention Call |
| Days since order > 20 | 🎁 Send Coupon |
| Hours on app < 1 | 📱 Push Notification |
| Order count < 2 | 🎁 First-Order Offer |
| City Tier 3 only | 👀 Monitor (not actionable) |
| New customer only | 👀 Monitor (not actionable) |
