# WORK OF CLARISSE BRET

from flask import Flask, render_template, jsonify
from best_day import best_day
from user_profile import User
import json

app = Flask(__name__)


@app.context_processor
def inject_user():
    user = User()
    name = "Kenza"
    query = user.get_user(name)
    dic = json.dumps(query, ensure_ascii=False)
    loaded_dic = json.loads(dic)
    return dict(mydict=loaded_dic)


@app.route("/")
def template():
    return render_template("template.html")


@app.route("/test2")
def test2():
    return render_template("test2.html")


@app.route('/resort_prediction', methods=['POST'])
def resort_prediction():
    forecast_date = "today"
    name = "Kenza"
    p = best_day(name, forecast_date)
    data = {"predicted_resort": p}
    data = jsonify(data)
    return data


if __name__ == "__main__":

    app.run(debug=True)
