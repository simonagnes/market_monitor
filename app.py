# import libraries
from dash import dcc, html, Dash, dash_table, callback, Input, Output, State, no_update
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dash_table.Format import Format, Symbol, Scheme
from dash.exceptions import PreventUpdate

import datetime
import base64
import io

# import components
from preprocess import preprocess_listings, preprocess_stats
from create_charts import *


css = [
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css",
]
app = Dash(
    name="Market Monitor",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

# load dataset
df = preprocess_stats("real_estate_stats_texas.csv")

df_current_listings = preprocess_listings("real_estate_broker_data_texas.csv")

df_own = df_current_listings[df_current_listings["brokered_by"] == 53016]
df_own["date_sold"] = pd.to_datetime(df_own["date_sold"])
df_recently_sold = (
    df_own[df_own["status"] == "sold"][
        [
            "date_sold",
            "street",
            "city",
            "zip_code",
            "price",
            "house_size",
            "bed",
            "bath",
            "acre_lot",
        ]
    ]
    .sort_values("date_sold", ascending=False)
    .head(7)
)
df_recently_sold["date_sold"] = pd.to_datetime(df_own["date_sold"]).dt.date
df_new_listings = (
    df_own[df_own["status"] == "for_sale"][
        [
            "date_published",
            "street",
            "city",
            "zip_code",
            "price",
            "house_size",
            "bed",
            "bath",
            "acre_lot",
        ]
    ]
    .sort_values("date_published", ascending=False)
    .head(7)
)


# create widgets

zips = df.postal_code.unique()

median_price = dcc.RadioItems(
    options={
        "median_listing_price": "Median Price",
        "median_listing_price_mm": "Price Change Previous Month",
        "median_listing_price_yy": "Price Change Previous Year",
    },
    value="median_listing_price",
    id="median",
    inline=True,
    style={"display": "flex", "flex-direction": "row", "gap": "20px"},
)
zip_select = dcc.Checklist(
    options=zips,
    value=["77546"],
    id="zips",
    inline=True,
    style={"display": "flex", "flex-direction": "row", "gap": "10px"},
)
zip_select_listings = dcc.Checklist(
    options=zips,
    value=["77546"],
    id="zips-listings",
    inline=True,
    style={"display": "flex", "flex-direction": "row", "gap": "10px"},
)
zip_select_current = dcc.Checklist(
    options=zips,
    value=["77546"],
    id="zips-current",
    inline=True,
    style={"display": "flex", "flex-direction": "row", "gap": "10px"},
)

listings = dcc.RadioItems(
    options={
        "total_listing_count": "Listings total",
        "total_listing_count_mm": "Listings previous month change",
        "total_listing_count_yy": "Listings previous year change",
    },
    value="total_listing_count",
    id="listings",
    inline=True,
    style={"display": "flex", "flex-direction": "row", "gap": "20px"},
)

price = 500000
bed = 5
bath = 5


# app layout

sidebar = html.Div(
    [
        html.Br(),
        html.Img(
            src="./assets/logo.jpg",
            alt="image",
            style={"width": "130%", "height": "auto", "margin-top": "63px"},
        ),
    ],
    className="col-2 text-black",
    style={"height": "100%"},
)

content = html.Div(
    [
        html.H1("Market Monitor", className="text-center fw-bold m-2"),
        html.Br(),
        dcc.Tabs(
            [
                # Dashboard tab
                dcc.Tab(
                    [
                        html.Br(),
                        html.Div(
                            [
                                # total sales this month
                                html.Div(
                                    [
                                        html.H5(
                                            "Total sales in "
                                            + str(
                                                datetime.datetime.now().strftime(
                                                    "%m/%Y"
                                                )
                                            )
                                        ),
                                        dcc.Markdown(
                                            f"**${total_sales(df_own):,.2f}**"
                                        ),  # Display revenue with formatting
                                    ],
                                    style={
                                        "flex": "1",
                                        "align-self": "center",
                                        "backgroundColor": "F2F2F2",
                                        "fontSize": 24,
                                        "text-align": "center",
                                    },
                                ),
                                # dash data table recent sales
                                html.Div(
                                    [
                                        html.H4("Recent sales"),
                                        dash_table.DataTable(
                                            data=df_recently_sold.to_dict("records"),
                                            columns=[
                                                {
                                                    "name": i,
                                                    "id": i,
                                                    "type": (
                                                        "numeric"
                                                        if i == "price"
                                                        else "text"
                                                    ),
                                                    "format": (
                                                        Format(
                                                            precision=2,
                                                            scheme=Scheme.fixed,
                                                            group=",",
                                                            symbol=Symbol.yes,
                                                            symbol_prefix="$",
                                                        )
                                                        if i == "price"
                                                        else None
                                                    ),
                                                }
                                                for i in df_recently_sold.columns
                                            ],
                                            style_table={
                                                "width": "100%",
                                                "marginRight": "20px",
                                                "backgroundColor": "blue",
                                            },
                                        ),
                                    ],
                                    style={"flex": "2", "backgroundColor": "grey"},
                                ),
                            ],
                            style={
                                "display": "block",
                                "flex-direction": "row",
                                "align-items": "center",
                            },
                        ),
                        html.Br(),
                        # dash data table New Listings
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H4("New Listings"),
                                        dash_table.DataTable(
                                            data=df_new_listings.to_dict("records"),
                                            columns=[
                                                {
                                                    "name": i,
                                                    "id": i,
                                                    "type": (
                                                        "numeric"
                                                        if i == "price"
                                                        else "text"
                                                    ),
                                                    "format": (
                                                        Format(
                                                            precision=2,
                                                            scheme=Scheme.fixed,
                                                            group=",",
                                                            symbol=Symbol.yes,
                                                            symbol_prefix="$",
                                                        )
                                                        if i == "price"
                                                        else None
                                                    ),
                                                }
                                                for i in df_new_listings.columns
                                            ],
                                            style_table={
                                                "width": "100%",
                                                "marginRight": "20px",  # Add margin to the right
                                                "backgroundColor": "#e98074",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "block",
                                        "backgroundColor": "grey",
                                        "width": "100%",
                                    },
                                ),
                            ],
                            className="box-shadow-container",
                            style={
                                "display": "block",
                                "flex-direction": "row",
                                "align-items": "center",
                            },
                        ),
                        html.Br(),
                        # sales value for last 3 months
                        html.Div(
                            [
                                html.Br(),
                                dcc.Graph(
                                    id="sales", figure=create_sales_chart(df_own)
                                ),
                            ],
                            style={
                                "flex": "1",
                                "align-self": "center",
                                "fontSize": 24,
                                "text-align": "center",
                            },
                        ),
                        html.Div(
                            [
                                # display number of current / active listings
                                html.Div(
                                    [
                                        html.H4("Active listings"),
                                        dcc.Markdown(
                                            f"**{current_number_of_listings(df_own)}**"
                                        ),  # display revenue with formatting
                                    ],
                                    className="box-shadow-container",
                                    style={
                                        "flex": "1",
                                        "align-self": "center",
                                        "fontSize": 24,
                                        "text-align": "center",
                                        "margin": "20px",
                                        "padding-top": "15px",
                                    },
                                ),
                                # display highest closing sum for this year
                                html.Div(
                                    [
                                        html.H4(
                                            "Highest closing in "
                                            + str(
                                                datetime.datetime.now().strftime("%Y")
                                            )
                                        ),
                                        dcc.Markdown(
                                            f"$**{highest_closing(df_own):,.2f}**"
                                        ),
                                    ],
                                    className="box-shadow-container",
                                    style={
                                        "flex": "1",
                                        "align-self": "center",
                                        "fontSize": 24,
                                        "text-align": "center",
                                        "margin": "20px",
                                        "padding-top": "15px",
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flex-direction": "row",
                                "align-items": "center",
                            },
                        ),
                        html.Div(
                            [
                                # number of listings sold last 3 months
                                html.Div(
                                    [
                                        html.H4("Sold last quarter"),
                                        dcc.Markdown(f"**{sold_last_quarter(df_own)}**"),
                                    ],
                                    className="box-shadow-container",
                                    style={
                                        "flex": "1",
                                        "align-self": "center",
                                        "fontSize": 24,
                                        "text-align": "center",
                                        "margin": "20px",
                                        "padding-top": "15px",
                                    },
                                ),
                                # dispaly median listing price
                                html.Div(
                                    [
                                        html.H4("Median price"),
                                        dcc.Markdown(
                                            f"$**{median_price_listings(df_own):,.2f}**"
                                        ),
                                    ],
                                    className="box-shadow-container",
                                    style={
                                        "flex": "1",
                                        "align-self": "center",
                                        "fontSize": 24,
                                        "text-align": "center",
                                        "margin": "20px",
                                        "padding-top": "15px",
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flex-direction": "row",
                                "align-items": "center",
                            },
                        ),
                        html.Div(
                            [
                                # display price distribution histogram
                                dcc.Graph(
                                    id="histogram",
                                    figure=create_price_histogram(df_own, "price"),
                                ),
                                html.Br(),
                                html.Br(),
                                html.Br(),
                                html.Br(),
                            ]
                        ),
                    ],
                    style={"display": "flex", "flex-direction": "column"},
                    label="Dashboard",
                ),
                # Price tab
                dcc.Tab(
                    [
                        html.Br(),
                        "Median Price",
                        median_price,
                        "Zip code",
                        zip_select,
                        html.Br(),
                        dcc.Graph(id="median-graph"),
                    ],
                    label="Price",
                ),
                # Listings tab
                dcc.Tab(
                    [
                        html.Br(),
                        "Listings",
                        listings,
                        "Zip code",
                        zip_select_listings,
                        html.Br(),
                        dcc.Graph(id="listings-graph"),
                    ],
                    label="Listings",
                ),
                # Current listings tab
                dcc.Tab(
                    [
                        html.Br(),
                        html.Br(),
                        html.Div(
                            [
                                html.Br(),
                                html.H5("Price"),
                                dcc.Slider(
                                    0,
                                    4000000,
                                    marks={
                                        100000: "100K",
                                        300000: "300K",
                                        500000: "500K",
                                        1000000: "1M",
                                        2000000: "2M",
                                        4000000: "5M",
                                    },
                                    value=500000,
                                    id="price",
                                    tooltip={
                                        "always_visible": True,
                                        "template": "$ {value}",
                                    },
                                ),
                                html.Br(),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.H5("Bedrooms"),
                                                dcc.Slider(
                                                    0, 5, 1, value=2, id="bedroom"
                                                ),
                                            ]
                                        ),
                                        dbc.Col(
                                            [
                                                html.H5("Bathrooms"),
                                                dcc.Slider(
                                                    0, 4, 1, value=1, id="bathroom"
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                                "Zip code",
                                zip_select_current,
                                html.Br(),
                            ]
                        ),
                        html.Div(
                            [
                                dcc.Graph(id="current-listings-graph"),
                                dcc.Location(id="url", refresh=True),
                                html.Br(),
                            ]
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id="filtered-listings",
                                    figure=create_filterd_listings_table(
                                        df_own, price, bed, bath
                                    ),
                                ),
                                html.Br(),
                            ]
                        ),
                    ],
                    label="Current Listings",
                ),
                # Upload tab
                dcc.Tab(
                    [
                        html.Br(),
                        "Upload",
                        html.Br(),
                        dcc.Upload(
                            id="upload-data",
                            children=html.Div(
                                ["Drag and Drop or ", html.A("Select Files")]
                            ),
                            style={
                                "width": "100%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "margin": "10px",
                            },
                            # Not allow multiple files to be uploaded
                            multiple=True,
                        ),
                        dcc.Store(id="store"),
                        html.Div(id="output-data-upload"),
                    ],
                    label="Upload",
                ),
            ]
        ),
    ],
    className="col-9 mx-auto",
    style={"height": "100vh"},
)


app.layout = html.Div(
    [html.Div([sidebar, content], className="row")],
    className="container-fluid",
    style={"height": "100%", "column-count": 2},
)

# callbacks


@callback(
    [Output("median-graph", "figure"), Output("zips", "value")],
    [Input("median", "value"), Input("zips", "value")],
)
def update_median_price_chart(median, zip):
    return create_median_price_chart(df, median, zip)


@callback(
    Output("listings-graph", "figure"),
    [Input("listings", "value"), Input("zips-listings", "value")],
)
def update_listings_chart(listings, zip):
    return create_listings_chart(df, listings, zip)


@callback(
    Output("current-listings-graph", "figure"),
    [
        Input("price", "value"),
        Input("bedroom", "value"),
        Input("bathroom", "value"),
        Input("zips-current", "value"),
    ],
)
def update_current_listings_chart(price, bed, bath, zip):
    return create_current_listings_chart(df_own, price, bed, bath, zip)


@callback(
    Output("filtered-listings", "figure"),
    [
        Input("price", "value"),
        Input("bedroom", "value"),
        Input("bathroom", "value"),
        Input("zips-current", "value"),
    ],
)
def update_filterd_listings_table(price, bed, bath, zip):
    return create_filterd_listings_table(df_own, price, bed, bath, zip)


@callback(
    Output("output-data-upload", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d)
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
        ]
        return children


# @app.callback(Output("download", "data"), [Input("btn", "n_clicks")])
# def func(n_clicks):
#     return send_file("/home/emher/Documents/Untitled.png")


@app.callback(Output("url", "href"), [Input("current-listings-graph", "clickData")])
def redirect_to_url(clickData):
    if clickData is None:
        return no_update
    # extract the URL from the clicked point
    point_url = clickData["points"][0]["customdata"][0]
    return point_url


if __name__ == "__main__":
    app.run(debug=True)
