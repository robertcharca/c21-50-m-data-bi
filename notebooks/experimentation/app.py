from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os
import sys
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

modelo_path = os.path.join(os.getcwd(), 'modelo_fraudev2.pkl')

# Cargar el modelo si existe
if os.path.exists(modelo_path):
    modelo = joblib.load(modelo_path)
else:
    print("Archivo de modelo no encontrado")
    sys.exit(1)

escalador = StandardScaler()

# Definir las columnas necesarias (las que se usaron para entrenar el modelo)
columnas_modelo = [
    "income", "name_email_similarity", "current_address_months_count", "customer_age",
    "days_since_request", "zip_count_4w", "velocity_6h", "velocity_24h", "velocity_4w",
    "bank_branch_count_8w", "date_of_birth_distinct_emails_4w", "credit_risk_score",
    "email_is_free", "phone_home_valid", "phone_mobile_valid", "bank_months_count",
    "has_other_cards", "proposed_credit_limit", "foreign_request", "session_length_in_minutes",
    "keep_alive_session", "device_distinct_emails_8w", "device_fraud_count", "month",
    "payment_type_AA", "payment_type_AB", "payment_type_AC", "payment_type_AD",
    "payment_type_AE", "employment_status_CA", "employment_status_CB", "employment_status_CC",
    "employment_status_CD", "employment_status_CE", "employment_status_CF", "employment_status_CG",
    "housing_status_BA", "housing_status_BB", "housing_status_BC", "housing_status_BD",
    "housing_status_BE", "housing_status_BF", "housing_status_BG", "source_INTERNET",
    "source_TELEAPP", "device_os_linux", "device_os_macintosh", "device_os_other",
    "device_os_windows", "device_os_x11"
]

def preparar_dataframe(df):
    # Filtrar solo las columnas que están en el modelo
    df_filtrado = df[columnas_modelo].copy()
    return df_filtrado

def preprocesar_datos(data_df):
    # Normalizar los datos o cualquier otro preprocesamiento necesario
    data_df_normalizado = escalador.fit_transform(data_df)
    return pd.DataFrame(data_df_normalizado, columns=data_df.columns)

@app.route('/')
def home():
    return "API de detección de fraudes está activa"

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No hay parte de archivo en la solicitud'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Archivo no cargado'}), 400
    
    data_df = pd.read_csv(file)

    # Preparar el DataFrame para que tenga solo las columnas necesarias
    data_df_preparado = preparar_dataframe(data_df)

    # Verificar el número de características después de preparar el DataFrame
    print(f"Número de características después de preparar: {data_df_preparado.shape[1]}")
    
    # Asegurarse de que el número de características coincida con lo que el modelo espera
    if data_df_preparado.shape[1] != 50:
        return jsonify({'error': f'Número de características incorrecto: se esperaban 50, pero se encontraron {data_df_preparado.shape[1]}'}), 400

    # Preprocesar los datos según lo necesite tu modelo
    data_df_preprocesado = preprocesar_datos(data_df_preparado)

    # Hacer predicciones
    prediccion = modelo.predict(data_df_preprocesado)

    # Convertir las predicciones a un formato json
    resultado = {'predicciones': prediccion.tolist()}
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)