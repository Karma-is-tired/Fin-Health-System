import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing
 
connection = sqlite3.connect("database/finance_tool.db")
df = pd.read_sql_query("SELECT * FROM transactions", connection)
connection.close()
 
df["txn_date"] = pd.to_datetime(df["txn_date"])
df["month"] = df["txn_date"].dt.to_period("M")
df["flow"] = df.apply(lambda row: row["amount"] if row["type"] == "income" else -row["amount"], axis=1)
monthly_net = df.groupby("month")["flow"].sum().sort_index()
 
print("Monthly net cash flow so far:")
print(monthly_net)
 
series = monthly_net.values.astype(float)
 
# ---- Method 1: Moving average ----
def moving_average_forecast(values, window=3):
    window = min(window, len(values))
    return values[-window:].mean()
 
# ---- Method 2: Linear regression on time ----
def linear_regression_forecast(values):
    x = np.arange(len(values)).reshape(-1, 1)
    model = LinearRegression().fit(x, values)
    next_x = np.array([[len(values)]])
    return model.predict(next_x)[0]
 
# ---- Method 3: Exponential smoothing (Holt-Winters) ----
def holt_winters_forecast(values):
    model = ExponentialSmoothing(values, trend="add").fit()
    return model.forecast(1)[0]
 
# ---- Backtest: hold out the most recent known month, see who predicts it best ----
train = series[:-1]
actual_last = series[-1]
 
candidates = {
    "moving_average": moving_average_forecast(train),
    "linear_regression": linear_regression_forecast(train),
    "holt_winters": holt_winters_forecast(train),
}
 
print("\nBacktest -- predicting the most recent known month from everything before it:")
errors = {}
for name, predicted in candidates.items():
    error = abs(predicted - actual_last)
    errors[name] = error
    print(f"  {name}: predicted {predicted:,.0f}, actual was {actual_last:,.0f}, error = {error:,.0f}")
 
best_method = min(errors, key=errors.get)
print(f"\nBest method on this data: {best_method}")
 
# ---- Forecast the next month for real, using ALL known data ----
final_candidates = {
    "moving_average": moving_average_forecast(series),
    "linear_regression": linear_regression_forecast(series),
    "holt_winters": holt_winters_forecast(series),
}
forecast = final_candidates[best_method]
 
print(f"\nMODULE 6 -- FORECAST for next month: {forecast:,.0f} (using {best_method})")
 
MIN_OPERATING_CASH = 100000
if forecast < MIN_OPERATING_CASH:
    print(f"WARNING: forecast is below the minimum operating cash threshold of {MIN_OPERATING_CASH:,.0f}")
else:
    print("Forecast is above the minimum operating cash threshold.")
