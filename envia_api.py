import requests

payload = {
    "age": 56,
    "Gender": "Male",
    "Weight": 88.3,
    "Height": 1.71,
    "Max_BPM": 180,
    "Avg_BPM": 157,
    "Resting_BPM": 60,
    "Session_Duration": 1.69,
    "Workout_Type": "Yoga",
    "Fat_Percentage": 12.6,
    "Water_Intake": 3.5,
    "Workout_Frequency": 4,
    "Experience_Level": 3,
    "BMI": 30.2
}

resposta=requests.post("http://ec2-34-224-22-47.compute-1.amazonaws.com:8080/predict",json=payload).json()

print(resposta)