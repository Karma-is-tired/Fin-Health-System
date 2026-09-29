import pandas as pd
import pandera as pa
from pandera import Column, Check
 
df = pd.read_csv("data/sample_transactions.csv")
 
# This mirrors the schema from Section 04 -- it's the rulebook every
# uploaded file has to pass before any module is allowed to touch it.
transaction_schema = pa.DataFrameSchema({
    "txn_date": Column(str),
    "amount": Column(float, Check(lambda s: s > 0), coerce=True),
    "type": Column(str, Check.isin(["income", "expense"])),
    "category": Column(str, nullable=True),
    "description": Column(str, nullable=True),
    "customer_vendor": Column(str, nullable=True),
    "account": Column(str, nullable=True),
})
 
try:
    validated = transaction_schema.validate(df, lazy=True)
    print(f"All {len(validated)} rows passed validation.")
except pa.errors.SchemaErrors as err:
    print("Some rows failed validation:")
    print(err.failure_cases)
 
