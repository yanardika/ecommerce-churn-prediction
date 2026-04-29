from flask import Flask, render_template, request
import numpy as np
import pickle
import json

app = Flask(__name__)

def churn_prediction(tenure, citytier, warehousetohome, gender, hourspendonapp,
                     numberofdeviceregistered, satisfactionscore, maritalstatus,
                     numberofaddress, complain, orderamounthikefromlastyear,
                     couponused, ordercount, daysincelastorder, cashbackamount):

    with open('models/churn_prediction_model.pkl', 'rb') as f:
        model = pickle.load(f)

    with open('models/columns.json', 'r') as f:
        data_columns = json.load(f)['data_columns']

    input_dict = {
        "tenure": tenure,
        "citytier": citytier,
        "warehousetohome": warehousetohome,
        "hourspendonapp": hourspendonapp,
        "numberofdeviceregistered": numberofdeviceregistered,
        "satisfactionscore": satisfactionscore,
        "numberofaddress": numberofaddress,
        "complain": complain,
        "orderamounthikefromlastyear": orderamounthikefromlastyear,
        "couponused": couponused,
        "ordercount": ordercount,
        "daysincelastorder": daysincelastorder,
        "cashbackamount": cashbackamount,
    }

    # Create a list of zeros for all columns
    input_array = np.zeros(len(data_columns))

    # Fill numeric values
    for i, col in enumerate(data_columns):
        if col in input_dict:
            input_array[i] = input_dict[col]

    # One-hot encode: gender
    gender_col = f"gender_{gender.lower()}"
    if gender_col in data_columns:
        input_array[data_columns.index(gender_col)] = 1

    # One-hot encode: marital status
    marital_col = f"maritalstatus_{maritalstatus.lower()}"
    if marital_col in data_columns:
        input_array[data_columns.index(marital_col)] = 1

    output_probab = model.predict_proba([input_array])[0][1]
    return round(output_probab, 4)


@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/predict', methods=['GET', 'POST'])
def index_page():
    if request.method == 'POST':
        form_data = request.form

        def to_num(val):
            try:
                return float(val)
            except ValueError:
                return val

        output_probab = churn_prediction(
            tenure=to_num(form_data['Tenure']),
            citytier=to_num(form_data['Citytier']),
            warehousetohome=to_num(form_data['Warehousetohome']),
            gender=form_data['Gender'],
            hourspendonapp=to_num(form_data['Hourspendonapp']),
            numberofdeviceregistered=to_num(form_data['Numberofdeviceregistered']),
            satisfactionscore=to_num(form_data['Satisfactionscore']),
            maritalstatus=form_data['Maritalstatus'],
            numberofaddress=to_num(form_data['Numberofaddress']),
            complain=to_num(form_data['Complain']),
            orderamounthikefromlastyear=to_num(form_data['Orderamounthikefromlastyear']),
            couponused=to_num(form_data['Couponused']),
            ordercount=to_num(form_data['Ordercount']),
            daysincelastorder=to_num(form_data['Daysincelastorder']),
            cashbackamount=to_num(form_data['Cashbackamount']),
        )

        pred = "Churn" if output_probab > 0.4 else "Not Churn"

        data = {
            'prediction': pred,
            'predict_probabality': output_probab
        }

        return render_template('result.html', data=data)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)