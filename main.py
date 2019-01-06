from flask import Flask, render_template
#from best_day import best_day

app = Flask(__name__)

@app.route("/")
def home():
    #forecast_date = '2019-01-04'
    #p = best_day(forecast_date)
    #return render_template("home.html", predicted_resort=p)
    return render_template("template.html")

@app.route("/about")
def about():
    return render_template("about.html")

# statsmodels
# pymongo
# pandas

@app.route("/salvador")
def salvador():
    return "Hello, Salvador"

if __name__ == "__main__":
    app.run(debug=True)