from flask import Flask, render_template, jsonify
from best_day import best_day
from weather_analysis import plot

app = Flask(__name__)

@app.route("/")
def template():
    return render_template("template.html")

@app.route('/resort_prediction', methods=['POST'])
def resort_prediction():
    forecast_date = '2019-01-04'
    p = best_day(forecast_date)
    data = {"predicted_resort": p}
    data = jsonify(data)
    return data

@app.route("/profile")
def profile():
    return render_template("profile.html")

if __name__ == "__main__":
    app.run(debug=True)
