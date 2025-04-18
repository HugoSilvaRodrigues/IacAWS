import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os



def modify_BMI(column):
    aux=[""]*len(column)
    for i in range(len(column)):
        if column[i]< 18.5:
            aux[i]="baixo_peso"
        elif column[i]>= 18.5 and column[i]<= 24.9:
            aux[i]="peso_normal"
        elif column[i]> 24.9 and column[i]<= 29.9:
            aux[i]="sobrepeso"
        elif column[i]> 29.9 and column[i]< 39.9:
            aux[i]="obesidade"
        elif column[i]> 39.9:
            aux[i]="obesidade_extrema"
    return aux

def categorical_to_number (atributos_train, atributos_teste, columns):
    encoder=OneHotEncoder(sparse_output=False)
    scaler=StandardScaler()
    X_train=pd.DataFrame(encoder.fit_transform(atributos_train[columns]))
    X_train.columns=encoder.get_feature_names_out(columns)
    train=pd.concat([pd.DataFrame(atributos_train).drop(columns,axis=1).reset_index(drop=True),X_train],axis=1)   
    X_test=pd.DataFrame(encoder.transform(atributos_teste[columns]))
    X_test.columns=encoder.get_feature_names_out(columns)
    test=pd.concat([pd.DataFrame(atributos_teste).drop(columns,axis=1).reset_index(drop=True),X_test],axis=1)   
    test.columns=test.columns.str.replace("Gender_ | Workout_Type_ |BMI_classe_","",regex=True)
    train.columns=train.columns.str.replace("Gender_ | Workout_Type_ |BMI_classe_","",regex=True)
    train=scaler.fit_transform(train)  
    test=scaler.transform(test)   
    return train,test,scaler,encoder
        

def main(filename):
    
    print("Iniciando o processo de processamento dos dados... \n")
    
    df=pd.read_csv(filename)
    
    df["BMI_classe"]=modify_BMI(df["BMI"])
    
    X=df.drop(["Calories_Burned","BMI"],axis=1)
    y=df["Calories_Burned"]
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42)
    categorical_columns=df.select_dtypes("object").columns
    
    os.makedirs("feature_store",exist_ok=True)
    train,test,scaler,encoder=categorical_to_number(X_train,X_test,categorical_columns)
    pd.DataFrame(train).to_csv("feature_store/feature_store/X_train.csv", index=False)
    y_train.to_csv("feature_store/feature_store/y_train.csv", index=False)
    pd.DataFrame(test).to_csv("feature_store/feature_store/X_test.csv", index=False)
    y_test.to_csv("feature_store/feature_store/y_test.csv", index=False)
    joblib.dump(scaler,"scaler.pkl")
    joblib.dump(encoder,"encoder.pkl")
    print("Processo de feature store concluido... \n")
