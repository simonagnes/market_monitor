import pandas as pd

# choose postal codes that are relevant
included_postal_codes = [
    77546,
    77573,
    77574,
    77581,
    77089,
    77598,
    77539,
    77517,
    77511,
    77062,
    77058,
]


def preprocess_listings(
    file="real_estate_broker_data_texas.csv",
    included_postal_codes=included_postal_codes,
):
    df = pd.read_csv(file)
    df = df[df["zip_code"].isin(included_postal_codes)]
    df["zip_code"] = df["zip_code"].astype(int).astype(str)
    df["date_sold"] = pd.to_datetime(df["date_sold"]).dt.strftime("%Y-%m-%d")
    df["date_published"] = pd.to_datetime(df["date_published"]).dt.strftime("%Y-%m-%d")
    return df


def preprocess_stats(
    file="real_estate_stats_texas.csv", included_postal_codes=included_postal_codes
):
    df = pd.read_csv(file)
    df = df[df["postal_code"].isin(included_postal_codes)]
    df["postal_code"] = df["postal_code"].astype(str)
    df.loc[:, "month_date_yyyymm"] = pd.to_datetime(
        df["month_date_yyyymm"].astype(str), format="%Y%m"
    )
    return df
