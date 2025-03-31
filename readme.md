🧠 Overview
This project was created as part of a BI case study for a grocery store client. The objective was to design an interactive tool that:

Visualizes sales and inventory by product and time

Highlights profitability and cost efficiency

Provides dynamic filters and breakdowns

Is intuitive for business and tech users alike

🚀 Features
Sales vs. Inventory Analysis by product and product type

Monthly Trends with profit %, margin, and toggles

Segmented Summaries: food/non-food, holiday/non-holiday

Custom Threshold Reporting

Cumulative Sales for Key Products

Cashflow Ratio by Week

🛠️ Tech Stack
Streamlit – for building the interactive dashboard

Pandas – for data manipulation

Plotly – for interactive charting

Python – core scripting

Folder Structure

ts_data_challenge/
├── app.py                 # Main app file
├── pages/                 # All dashboard sections
├── utils/                 # Data loading & merging logic
├── data/                  # Input CSV files
├── requirements.txt       # Package dependencies
└── README.md              # You're here!


Getting Started

1. Clone this repo 
git clone https://github.com/anujseth1/ts_data_challenge.git
cd ts_data_challenge

2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # on Windows
# OR
source venv/bin/activate  # on Mac/Linux

3. Install dependencies
pip install -r requirements.txt

4. Run the dashboard
streamlit run app.py

🔐 Access & Deployment
This repository is public.

You can also view the deployed dashboard on Streamlit Cloud (link to be added once deployed).

🧾 License
This project is provided for demo purposes and is not licensed for commercial use.
