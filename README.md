# 📉 ChurnInsight Dashboard

### AI-Powered Customer Churn Prediction & Retention Intelligence Platform

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Railway-blueviolet?style=for-the-badge)](https://customer-churn-production-4ac0.up.railway.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Plotly Dash](https://img.shields.io/badge/Plotly_Dash-2.0+-00CC96?style=for-the-badge&logo=plotly&logoColor=white)](https://dash.plotly.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-ML_Model-FF6600?style=for-the-badge&logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io)
[![Claude AI](https://img.shields.io/badge/Anthropic_Claude-AI_Chat-6B4FBB?style=for-the-badge)](https://anthropic.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

> **Predict which customers will leave — before they do.**  
> A full-stack ML dashboard combining XGBoost prediction, interactive analytics, and Anthropic Claude AI for actionable retention strategies.

**[🌐 Try it Live →](https://customer-churn-production-4ac0.up.railway.app/)**

</div>

---

## 📸 Demo

> *(Add a GIF or screenshot of the dashboard here)*  
> `![Dashbo<img width="1920" height="1030" alt="Screenshot 2026-05-29 194743" src="https://github.com/user-attachments/assets/a389568b-7537-4532-b1c3-55d9e621d1fe" />
ard Preview](assets/demo.gif)`

---

## 🧠 What Is This?

**ChurnInsight** is an end-to-end customer churn prediction system built for e-commerce businesses. It answers two critical questions:

1. **Who is about to leave?** — XGBoost ML model predicts churn probability for each customer.
2. **What should we do about it?** — A built-in recommendation engine + Claude AI chat suggests tailored retention actions.

### Key Differentiators
- 🤖 **AI Chat Integration** — Ask Claude AI anything about a specific customer's churn risk
- 📊 **6 Interactive Charts** — Visual breakdown of churn by city tier, tenure, complaints, and more
- ⚡ **Batch Processing** — Upload thousands of customers at once via CSV
- 🎯 **Actionable Retention Logic** — Automatic rules engine maps risk to real business actions
- 📥 **Export Results** — Download predictions + recommendations as CSV

---

## 🏗️ Architecture & Tech Stack

```
ChurnInsight/
├── app.py                 ← Dash app entry point & server config
├── layout.py              ← UI layout & component structure
├── callbacks.py           ← All interactive logic & predictions
├── charts.py              ← 6 Plotly chart builders
├── recommendations.py     ← Retention action rules engine
├── config.py              ← App configuration & constants
├── xgb_churn_model.pkl    ← Pre-trained XGBoost model
├── requirements.txt       ← Python dependencies
├── assets/
│   └── style.css          ← Custom dark theme
└── DS_Project (1).ipynb   ← EDA & model training notebook
```

| Layer | Technology |
|---|---|
| **Frontend** | Plotly Dash, HTML/CSS |
| **Backend** | Python, Dash Callbacks |
| **ML Model** | XGBoost Classifier |
| **AI Integration** | Anthropic Claude API |
| **Deployment** | Railway |
| **Data Analysis** | Pandas, NumPy, Jupyter |

---

## ✨ Features

### 🔍 Tab 1 — Single Customer Prediction
Enter a customer's profile and get:
- **Churn probability** displayed on a real-time gauge chart
- **Risk classification**: Low / Medium / High
- **Recommended retention action** (see logic below)
- **AI Chat** — Interact with Claude about this specific customer

### 📦 Tab 2 — Batch Analysis
Upload a CSV file and get:

| Chart | Insight |
|---|---|
| 🍩 Risk Distribution Donut | Overall churn risk breakdown |
| 📊 Churn by City Tier | Which cities have highest risk |
| ⚖️ Churn vs Complaint | Impact of complaints on churn |
| 📈 Churn by Tenure | How long customers stay before leaving |
| 🔵 Hours Spent vs Risk | Engagement level correlation |
| 📉 Risk Score Distribution | Histogram of predicted probabilities |

Plus: sortable results table + **CSV export** of all predictions.

---

## 🎯 Retention Recommendation Logic

| Customer Condition | Recommended Action |
|---|---|
| Has complained | 📞 Priority Retention Call |
| Days since last order > 20 | 🎁 Send Coupon / Discount |
| Hours on app < 1/day | 📱 Re-engagement Push Notification |
| Order count < 2 | 🎁 First-Order Incentive Offer |
| City Tier 3 only | 👀 Monitor — Limited action available |
| New customer (< 3 months) | 👀 Monitor — Onboarding check |

---

## 📂 Input CSV Format

Your CSV must contain these columns (flexible naming supported):

| Column | Type | Example |
|---|---|---|
| `Tenure` | Integer | `12` |
| `CityTier` | Integer (1/2/3) | `1` |
| `HourSpendOnApp` | Float | `3.5` |
| `NumberOfDeviceRegistered` | Integer | `2` |
| `Complain` | Binary (0/1) | `0` |
| `OrderCount` | Integer | `5` |
| `DaySinceLastOrder` | Integer | `7` |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Anthropic API Key → [Get yours here](https://console.anthropic.com)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/maryhansabry/customer-churn.git
cd customer-churn

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your Anthropic API key
export ANTHROPIC_API_KEY=your_key_here        # Mac/Linux
# set ANTHROPIC_API_KEY=your_key_here         # Windows

# 5. Run the app
python app.py
```

Open your browser at → **http://localhost:8050**

---

## 🤖 ML Model Details

The churn prediction model was trained on e-commerce customer data using:

- **Algorithm**: XGBoost Classifier
- **Key Features**: Tenure, City Tier, App usage hours, Device count, Complaints, Order history
- **Notebook**: See Customer_churn_analysis.ipynb` for full EDA, feature engineering, and training pipeline

> To retrain on your own data, run all cells in the Jupyter Notebook and replace `xgb_churn_model.pkl` with your new model file.

---

## 🌍 Deployment

This app is deployed on **Railway** and accessible at:  
🔗 [https://customer-churn-production-4ac0.up.railway.app/](https://customer-churn-production-4ac0.up.railway.app/)

To deploy your own instance:
1. Fork this repository
2. Create a new project on [Railway](https://railway.app)
3. Connect your GitHub repo
4. Add `ANTHROPIC_API_KEY` as an environment variable
5. Deploy 🚀

---

## 🔮 Future Improvements

- [ ] Add user authentication & login system
- [ ] Support more ML models (LightGBM, CatBoost) with comparison
- [ ] Real-time data streaming integration
- [ ] Email/Slack notification system for high-risk customers
- [ ] Multi-language support (Arabic / English)
- [ ] Add unit tests & CI/CD pipeline via GitHub Actions

---

## 📜 License

This project is open source — feel free to use, modify, and build on it.  
See the [LICENSE](LICENSE) file for details.

---

<div align="center">

⭐ **If this project helped you, consider giving it a star!** ⭐

</div>
