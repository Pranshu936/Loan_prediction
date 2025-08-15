from flask import Flask, render_template, request
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# Load model and scaler
with open("loan_prediction_model.pkl", "rb") as f:
    model = pickle.load(f)

# NOTE: You would need to create and save this scaler from your notebook
# For example:
# scaler = StandardScaler()
# X_train_scaled = scaler.fit_transform(X_train)
# with open("scaler.pkl", "wb") as f:
#     pickle.dump(scaler, f)

with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)


# Order of features as in training
FEATURE_ORDER = [
    'ApplicantIncome', 'CoapplicantIncome', 'LoanAmount', 'Loan_Amount_Term', 'Credit_History',
    'Gender_Male', 'Married_Yes',
    'Dependents_1', 'Dependents_2', 'Dependents_3+',
    'Education_Not Graduate', 'Self_Employed_Yes',
    'Property_Area_Semiurban', 'Property_Area_Urban'
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/prediction", methods=["POST"])
def prediction():
    try:
        # ----- Numeric features -----
        appl_inc = float(request.form["ApplicantIncome"])
        coappl_inc = float(request.form["CoapplicantIncome"])
        loan_am = float(request.form["LoanAmount"])
        loan_am_tr = float(request.form["Loan_Amount_Term"])
        cred_hist = 1 if request.form["Credit_History"] == "Yes" else 0

        # ----- Gender dummy -----
        gender_male = 1 if request.form["gender"] == "Male" else 0

        # ----- Married dummy -----
        married_yes = 1 if request.form["Married"] == "Yes" else 0

        # ----- Dependents dummies -----
        dep_input = request.form["Dependents"]
        dep_1 = 1 if dep_input == "1" else 0
        dep_2 = 1 if dep_input == "2" else 0
        dep_3plus = 1 if dep_input == "3+" else 0

        # ----- Education dummy -----
        edu_notgrad = 1 if request.form["Education"] == "Not Graduate" else 0

        # ----- Self Employed dummy -----
        selfemp_yes = 1 if request.form["Self_employed"] == "Yes" else 0

        # ----- Property Area dummies -----
        prop_area = request.form["Property_Area"]
        prop_semiurban = 1 if prop_area == "Semi Urban" else 0
        prop_urban = 1 if prop_area == "Urban" else 0

        # Create feature dict to ensure correct ordering
        feature_dict = {
            'ApplicantIncome': appl_inc,
            'CoapplicantIncome': coappl_inc,
            'LoanAmount': loan_am,
            'Loan_Amount_Term': loan_am_tr,
            'Credit_History': cred_hist,
            'Gender_Male': gender_male,
            'Married_Yes': married_yes,
            'Dependents_1': dep_1,
            'Dependents_2': dep_2,
            'Dependents_3+': dep_3plus,
            'Education_Not Graduate': edu_notgrad,
            'Self_Employed_Yes': selfemp_yes,
            'Property_Area_Semiurban': prop_semiurban,
            'Property_Area_Urban': prop_urban
        }

        # Arrange features in training order
        features = np.array([feature_dict[col] for col in FEATURE_ORDER]).reshape(1, -1)

        # ***FIX: Scale the features before prediction***
        scaled_features = scaler.transform(features)

        # Predict
        prediction = model.predict(scaled_features)[0]
        output = "Yes" if prediction == 1 else "No"

        return render_template("index.html", pred_text=f"Loan Approved? {output}")

    except Exception as e:
        return render_template("index.html", pred_text=f"Error: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)