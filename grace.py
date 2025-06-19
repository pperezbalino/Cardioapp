import math

def calculate_grace_score(age, heart_rate, systolic_bp, creatinine, killip_class,
                          cardiac_arrest, st_depression, elevated_troponin):
    """
    Calcula el GRACE risk score y estima el riesgo de mortalidad intrahospitalaria.
    Parámetros:
        - age: Edad en años
        - heart_rate: Frecuencia cardíaca (latidos por minuto)
        - systolic_bp: Presión arterial sistólica (mmHg)
        - creatinine: Creatinina sérica (mg/dL)
        - killip_class: Clase de Killip (1 a 4)
        - cardiac_arrest: Paro cardíaco en admisión (bool)
        - st_depression: Depresión del ST en ECG (bool)
        - elevated_troponin: Troponina elevada (bool)
    """
    score = 0

    # Edad
    if age < 30:
        score += 0
    elif age < 40:
        score += 8
    elif age < 50:
        score += 25
    elif age < 60:
        score += 41
    elif age < 70:
        score += 58
    elif age < 80:
        score += 75
    else:
        score += 91

    # Frecuencia cardíaca
    if heart_rate < 50:
        score += 0
    elif heart_rate < 70:
        score += 3
    elif heart_rate < 90:
        score += 9
    elif heart_rate < 110:
        score += 15
    elif heart_rate < 150:
        score += 24
    else:
        score += 38

    # PAS
    if systolic_bp > 200:
        score += 0
    elif systolic_bp > 180:
        score += 5
    elif systolic_bp > 160:
        score += 10
    elif systolic_bp > 140:
        score += 17
    elif systolic_bp > 120:
        score += 24
    elif systolic_bp > 100:
        score += 31
    elif systolic_bp > 80:
        score += 39
    else:
        score += 48

    # Creatinina
    if creatinine < 1:
        score += 1
    elif creatinine < 1.5:
        score += 4
    elif creatinine < 2:
        score += 7
    elif creatinine < 3:
        score += 10
    else:
        score += 13

    # Killip
    score += {1: 0, 2: 20, 3: 39, 4: 59}.get(killip_class, 0)

    # Paro
    if cardiac_arrest:
        score += 39

    # ST depression
    if st_depression:
        score += 28

    # Troponina
    if elevated_troponin:
        score += 14

    # Estratificación
    if score < 109:
        risk_class = "Bajo"
    elif score < 140:
        risk_class = "Moderado"
    else:
        risk_class = "Alto"

    return score, risk_class
