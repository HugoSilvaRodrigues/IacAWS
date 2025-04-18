from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import uvicorn

from feature_store.criacao_feature_store import modify_BMI
import pandas as pd

app=FastAPI(title="api previsao de calorias",
            contact="hugosilvarodrigues@gmail.com")

class Features(BaseModel):
    age: int;
    Gender: str;
    Weight: float;
    Height: float;
    Max_BPM: int;
    Avg_BPM: int;
    Resting_BPM	: int;
    Session_Duration : float;
    Workout_Type: str;
    Fat_Percentage:	float;
    Water_Intake : float;
    Workout_Frequency : int;
    Experience_Level: int;
    BMI: float;
    
@app.post('/predict')
async def predict(request_data:Features):
    model=joblib.load("model.pkl")
    scaler=joblib.load("scaler.pkl")
    encoder=joblib.load("encoder.pkl")
    
    request_dict = {
        "Age": [request_data.age],
        "Gender": [request_data.Gender],
        "Weight (kg)": request_data.Weight,
        "Height (m)": request_data.Height,
        "Max_BPM": [request_data.Max_BPM],
        "Avg_BPM": [request_data.Avg_BPM],
        "Resting_BPM": [request_data.Resting_BPM],
        "Session_Duration (hours)": [request_data.Session_Duration],
        "Workout_Type": [request_data.Workout_Type],
        "Fat_Percentage": [request_data.Fat_Percentage],
        "Water_Intake (liters)": [request_data.Water_Intake],
        "Workout_Frequency (days/week)": [request_data.Workout_Frequency],
        "Experience_Level": [request_data.Experience_Level],
        "BMI": [request_data.BMI]
    }
    
    request_data=pd.DataFrame(request_dict)
    request_data["BMI_classe"]=modify_BMI(request_data["BMI"])
    encoded_data=pd.DataFrame(encoder.transform(request_data[["Gender","Workout_Type","BMI_classe"]]))
    encoded_data.columns=encoder.get_feature_names_out(["Gender","Workout_Type","BMI_classe"])
    request_data=pd.concat([request_data.drop(["Gender","Workout_Type","BMI","BMI_classe"],axis=1).reset_index(drop=True),encoded_data],axis=1)
    request_data.columns=request_data.columns.str.replace("Gender_ | Workout_Type_ |BMI_classe_","",regex=True)
    formated_data=scaler.transform(request_data)
    
    try:
        pred=model.predict(formated_data)
    except:
        print("Erro no momento de realizar a previsao")
    return pred[0]

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0",port=8080)
