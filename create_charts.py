# import libraries
from dash import dcc, html, Dash, dash_table, callback, Input, Output, State, no_update

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
import datetime
import base64
import io

# create charts and tables


# table 1 dashboard
# display total sales in this month
def total_sales(df_own):
    df_filtered = df_own[
        (df_own["date_sold"] > str(pd.Timestamp.now().replace(day=1)))
        & (df_own["date_sold"] < str(pd.Timestamp.now()))
        & (df_own["status"] == "sold")
    ]

    return df_filtered["price"].astype(float).sum()


# previous 3 months sales chart (bar)
def create_sales_chart(df_own):
    # Get the revenue data for the last 3 months
    sales = get_sales_last_n_months(df_own, "date_sold")

    # Create the bar chart using Plotly Express
    fig = px.bar(
        sales,
        x="month",
        y="sales",
        title="Monthly Revenue",
        # labels={'date_sold': 'Month', 'price': 'Revenue'},
        text_auto=True,
    )
    # Update the x-axis to display only the month and year
    fig.update_layout(
        xaxis=dict(
            type='category',
            tickformat='%b-%Y'  # Format the tick labels to show month and year only
        ),
        xaxis_title='Month',
        yaxis_title='Values',
        title='Monthly Sales Value'
    )
    return fig


def get_sales_last_n_months(df, date_column):
    # get the current date
    now = pd.Timestamp.now()

    # calculate the first day of the current month
    first_day_current_month = now.replace(day=1)

    # calculate the first day of the month 1 and 2 months before
    first_day_1_months_ago = (
        first_day_current_month - pd.DateOffset(months=1)
    ).replace(day=1)
    first_day_2_months_ago = (
        first_day_current_month - pd.DateOffset(months=2)
    ).replace(day=1)

    # sum the sales value for each of the 3 previous months

    this_month_sales = df.loc[
        (df[date_column] >= first_day_current_month) & (df[date_column] <= now)
    ]["price"].sum()
    prev_month_sales = df.loc[
        (df[date_column] >= first_day_1_months_ago)
        & (df[date_column] < first_day_current_month)
    ]["price"].sum()
    prev2_month_sales = df.loc[
        (df[date_column] >= first_day_2_months_ago)
        & (df[date_column] < first_day_1_months_ago)
    ]["price"].sum()

    return pd.DataFrame(
        [
            {
                "month": str(first_day_2_months_ago.year)
                + "-"
                + str(first_day_2_months_ago.month),
                "sales": prev2_month_sales,
            },
            {
                "month": str(first_day_1_months_ago.year)
                + "-"
                + str(first_day_1_months_ago.month),
                "sales": prev_month_sales,
            },
            {"month": str(now.year) + "-" + str(now.month), "sales": this_month_sales},
        ],
        index=[1, 2, 3],
    )


# dispaly number of current / active listings
def current_number_of_listings(df_own):
    number_of_listings = df_own["status"].value_counts().get("for_sale", 0)

    return number_of_listings


def create_table(df_current_listings):
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(values=df_current_listings.columns[2:8], align="left"),
                cells=dict(values=df_current_listings.values.T[2:8], align="left"),
            )
        ]
    )
    fig.update_layout(
        paper_bgcolor="white", margin={"t": 0, "l": 0, "r": 0, "b": 0}, height=700
    )
    return fig


# return highest closing sum
def highest_closing(df_own):
    highest = df_own[df_own["status"] == "sold"]["price"].max()
    return highest


# return number of listings sold last quarter
def sold_last_quarter(df_own):
    past_quarter_begins = pd.Timestamp.now() - pd.DateOffset(months=3)
    return df_own[
        (df_own["status"] == "sold") & (df_own["date_sold"] > past_quarter_begins)
    ].shape[0]


def median_price_listings(df_own):
    return df_own["price"].median()


def create_price_histogram(df_own, col_name):
    fig = px.histogram(
        df_own,
        title="Price distribution",
        x=col_name,
        nbins=12,
        color="city",
        color_discrete_sequence=[
            "#2E86AB",
            "#F6D55C",
            "#3CAEA3",
            "#ED553B",
            "#173F5F",
            "#20639B",
            "#E94E77",
            "#F6AB6C",
            "#96CEB4",
            "#5D5C61",
        ],
    )
    fig.update_traces(marker={"line": {"width": 2, "color": "white"}})
    fig.update_layout(paper_bgcolor="white")
    return fig


# table 2 price
def create_median_price_chart(df, col_chosen, zip_selected):
    filtered_df = df[df["postal_code"].isin(zip_selected)]

    fig = px.scatter(
        filtered_df,
        x="month_date_yyyymm",
        y=col_chosen,
        labels={"month_date_yyyymm": "Date", col_chosen: "Price", "zip_name": "City"},
        color="zip_name",
        hover_data=["median_listing_price"],
        trendline="lowess",
    )
    fig.update_layout(paper_bgcolor="white", height=600)
    return fig, zip_selected

# table 3 listings
def create_listings_chart(df, col_chosen, zip_selected=["77546"]):
    filtered_df = df[df["postal_code"].isin(zip_selected)]

    fig = px.scatter(
        filtered_df,
        x="month_date_yyyymm",
        y=col_chosen,
        labels={"month_date_yyyymm": "Date", col_chosen: "Count", "zip_name": "City"},
        color="zip_name",
    )
    fig.update_layout(paper_bgcolor="white", height=600)
    return fig

# table 4 listings
def create_current_listings_chart(
    df_current_listings, price, bed, bath, zip_selected=["77546"]
):
    filtered_df = df_current_listings[
        (df_current_listings["zip_code"].isin(zip_selected))
        & (df_current_listings["price"] <= price)
        & (df_current_listings["bed"] >= bed)
        & (df_current_listings["bath"] >= bath)
    ]
    filtered_df.sort_values(by="price", ascending=True, inplace=True)

    fig = px.scatter(
        filtered_df,
        x="house_size",
        y="price",
        labels={"house_size": "House size", "price": "Price", "zip_code": "Zip code"},
        color="zip_code",
        custom_data=["links"],
    )
    fig.update_layout(paper_bgcolor="white", height=450)
    return fig


def create_filterd_listings_table(df_current_listings, price, bed, bath, zip=["77546"]):
    filtered_df = df_current_listings[
        (df_current_listings["price"] <= price)
        & (df_current_listings["bed"] >= bed)
        & (df_current_listings["bath"] >= bath)
        & (df_current_listings["zip_code"].isin(zip))
    ]
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=filtered_df[
                        [
                            "zip_code",
                            "city",
                            "street",
                            "price",
                            "house_size",
                            "bed",
                            "bath",
                            "acre_lot",
                            # "links",
                        ]
                    ].columns[:],
                    align="left",
                ),
                cells=dict(
                    values=filtered_df[
                        [
                            "zip_code",
                            "city",
                            "street",
                            "price",
                            "house_size",
                            "bed",
                            "bath",
                            "acre_lot",
                            # "links",
                        ]
                    ].values.T[:],
                    align="left",
                ),
            )
        ]
    )
    fig.update_layout(
        paper_bgcolor="white", margin={"t": 0, "l": 0, "r": 0, "b": 0}, height=300
    )

    return fig


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV file
            df_upload = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df_upload = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    return html.Div(
        [
            html.H5(filename),
            html.H6(datetime.datetime.fromtimestamp(date)),
            dash_table.DataTable(
                df_upload.iloc[:10, 2:10].to_dict("records"),
                [{"name": i, "id": i} for i in df_upload.iloc[:10, 2:10].columns],
            ),
            html.Hr(),  # horizontal line
        ]
    )
