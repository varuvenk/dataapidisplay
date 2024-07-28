import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///EconomicData.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class EconomicData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(80))
    value = db.Column(db.Float)

    def __init__(self, date, value):
        self.date = date
        self.value = value

def fetch_economic_data():
    # Replace 'your_api_key' with your actual FRED API key
    api_key = '7a82d62d6c11d9c79fd7045a9aa5d7d3'
    series_id = 'GDP'  # You can replace this with any FRED series ID
    response = requests.get(f'https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json')
    print(f"API Response Status Code: {response.status_code}")  # Debugging statement
    if response.status_code == 200:
        data = response.json()['observations']
        print(f"Fetched Data: {data}")  # Debugging statement
        valid_data = []
        for obs in data:
            try:
                date = obs['date']
                value = float(obs['value'])
                valid_data.append((date, value))
            except ValueError:
                print(f"Invalid data found: {obs['value']}, skipping entry")  # Debugging statement
        return valid_data
    else:
        print(f"Error fetching data: {response.text}")  # Debugging statement
        return []

def save_data_to_db(data):
    for date, value in data:
        new_entry = EconomicData(date=date, value=value)
        db.session.add(new_entry)
    db.session.commit()

@app.before_request
def before_request_func():
    if not EconomicData.query.first():
        data = fetch_economic_data()
        save_data_to_db(data)

@app.route('/')
def index():
    data = EconomicData.query.all()
    return {
        "economic_data": [{
            "date": entry.date,
            "value": entry.value
        } for entry in data]
    }

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=False)

