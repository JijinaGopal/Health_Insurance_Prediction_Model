import streamlit as st
import pickle
import pandas as pd


# Load trained model
with open("claim_model.pkl", "rb") as file:
    lR = pickle.load(file)

# Load encoder
with open("label_encoder.pkl", "rb") as file:
    lb = pickle.load(file)


# User
USER_CREDENTIALS = {
    "admin": "admin123",
    "user": "user123"
}  



def login():
    st.title("🔐 Login to Claim Prediction App")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")


    if login_btn:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid username or password")


def predict_page():
    st.title("📑 Claim Status Prediction")

    # Input form
    with st.form("claim_form"):
        claim_amount = st.number_input("ClaimAmount", min_value=0.0)
        diagnosis = st.selectbox("DiagnosisCode",lb["DiagnosisCode"].classes_)
        procedure = st.selectbox("ProcedureCode",lb["ProcedureCode"].classes_)
        age = st.number_input("PatientAge", min_value=0, max_value=120)
        gender = st.selectbox("PatientGender", ["M", "F"])
        specialty = st.selectbox("ProviderSpecialty",["Cardiology", "Pediatrics", "Neurology", "General Practice","Orthopedics"])
        income = st.number_input("PatientIncome", min_value=0.0)
        marital = st.selectbox("PatientMaritalStatus",["Single", "Married", "Divorced", "Widowed"])
        employment = st.selectbox("Patient Employment Status", ["Employed", "Unemployed", "Retired", "Student"])
        location = st.selectbox("ProviderLocation",lb["ProviderLocation"].classes_)
        claim_type = st.selectbox("ClaimType", ["Inpatient", "Outpatient", "Emergency", "Routine"])
        submission = st.selectbox("ClaimSubmissionMethod", ["Online", "Paper", "Phone"])
        year = st.number_input("Year", min_value=2000, max_value=2100, step=1)
        month = st.number_input("Month", min_value=1, max_value=12, step=1)
        day = st.number_input("Day",min_value=1, max_value=31, step=1)

        submit = st.form_submit_button("Predict")



    if submit:
        if lR is None:
            st.error("⚠️ No model found. Please train and save 'claim_model.pkl'.")
            return

        # Prepare input as DataFrame
        input_data = pd.DataFrame([{
            "ClaimAmount": claim_amount,
            "DiagnosisCode": diagnosis,
            "ProcedureCode": procedure,
            "PatientAge": age,
            "PatientGender": gender,
            "ProviderSpecialty": specialty,
            "PatientIncome": income,
            "PatientMaritalStatus": marital,
            "PatientEmploymentStatus": employment,
            "ProviderLocation": location,
            "ClaimType": claim_type,
            "ClaimSubmissionMethod": submission,
            "Year": year,
            "Month": month,
            "Weekday": day
        }])

         #Apply label encoder to categorical columns
        for col, encoder in lb.items():
            if col in input_data.columns:
                try:
                    input_data[col] = encoder.transform(input_data[col])
                except ValueError:
                    st.error(f"⚠️ Value '{input_data[col][0]}' not seen during training for column '{col}'")
                    return

        # Predict
        prediction = lR.predict(input_data)[0]
        st.subheader("Prediction Result")
        if prediction == 0:
            st.success("✅ Claim Approved")
        else:
            st.error("❌ Claim Denied")


# -----------------------------
# Main App Flow
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    #Sidebar logout option
    with st.sidebar:
        if "username" in st.session_state:
            st.write(f"👤 Logged in as: {st.session_state['username']}")

        if st.button("🚪 Logout"):
            st.session_state["logged_in"] = False
            st.session_state.pop("username", None)
      

    # Show prediction page
    predict_page()