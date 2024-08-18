# Market Monitor


## Description
The Market Monitor Real Estate Broker Dashboard is an internal tool designed for real estate brokers to efficiently visualize and analyze their real estate listings and sales data. This dashboard helps brokers make informed decisions by providing insights into the latest listings, active listings, and sales values over different periods. Additionally, it offers detailed statistics on pricing and the number of listings across various ZIP codes.

### Key Features

- Newest and Active Listings Overview:
    - Displays the latest property listings and active ones, allowing brokers to keep track of the inventory.

- Sales Value Analysis:
    - Visualizes sales data from previous periods, enabling brokers to track performance and trends.

- ZIP Code Statistics:
    - Shows detailed statistics for different ZIP codes, including the number of listings and median prices.
    - Interactive feature to filter and visualize median prices for selected ZIP codes using checkboxes.

- Current Listings Tab:
    - Provides a sortable table of the current listings from the brokerage.
    - Users can sort by price, number of bathrooms, or bedrooms to find relevant properties quickly.

- Interactive Scatterplot:
    - Scatterplot visualization of listings where each point represents a property.
    - Clicking on a point opens the corresponding Zillow page for that listing, offering quick access to more detailed information.


## Demo
Check out the [live demo](https://youtu.be/s1MA_nJ-hvo).
## Installation
### Prerequisites
  - Python 3
  - pip
### Clone the Repository
```bash
git clone https://github.com/simonagnes/market_monitor.git
```
### Install dependecies
```python
pip install -r requirements.txt
```
## Usage
### Running the app
```python
python app.py
```
### Accessing the app
  - open a browser and go to http://127.0.0.1:8050/

## File structure
```
├── assets/
├── app.py
├── create_charts.py
├── preprocess.py
├── real_estate_broker_data_texas.csv
├── real_estate_stats_texas.csv
├── requirements.txt
└── README.md
```
