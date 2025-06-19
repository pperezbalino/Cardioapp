
def calculate_framingham_score(age, gender, total_chol, hdl, systolic_bp, smoker, diabetic, on_treatment):
    # Asignación de puntos basada en ATP III Framingham Score
    points = 0
    if gender == 'male':
        if age < 35:
            points += -9
        elif age < 40:
            points += -4
        elif age < 45:
            points += 0
        elif age < 50:
            points += 3
        elif age < 55:
            points += 6
        elif age < 60:
            points += 8
        elif age < 65:
            points += 10
        elif age < 70:
            points += 11
        else:
            points += 12

        if smoker:
            if age < 40:
                points += 8
            elif age < 50:
                points += 5
            elif age < 60:
                points += 3
            elif age < 70:
                points += 1
            else:
                points += 1

        if total_chol < 160:
            points += 0
        elif total_chol < 200:
            points += 1
        elif total_chol < 240:
            points += 2
        elif total_chol < 280:
            points += 3
        else:
            points += 4

        if hdl >= 60:
            points += -1
        elif hdl < 40:
            points += 2
        elif hdl < 50:
            points += 1

        if on_treatment:
            if systolic_bp < 120:
                points += 0
            elif systolic_bp < 130:
                points += 1
            elif systolic_bp < 140:
                points += 2
            elif systolic_bp < 160:
                points += 2
            else:
                points += 3
        else:
            if systolic_bp < 120:
                points += 0
            elif systolic_bp < 130:
                points += 0
            elif systolic_bp < 140:
                points += 1
            elif systolic_bp < 160:
                points += 1
            else:
                points += 2

    else:  # Female
        if age < 35:
            points += -7
        elif age < 40:
            points += -3
        elif age < 45:
            points += 0
        elif age < 50:
            points += 3
        elif age < 55:
            points += 6
        elif age < 60:
            points += 8
        elif age < 65:
            points += 10
        elif age < 70:
            points += 12
        else:
            points += 14

        if smoker:
            if age < 40:
                points += 9
            elif age < 50:
                points += 7
            elif age < 60:
                points += 4
            elif age < 70:
                points += 2
            else:
                points += 1

        if total_chol < 160:
            points += 0
        elif total_chol < 200:
            points += 1
        elif total_chol < 240:
            points += 3
        elif total_chol < 280:
            points += 4
        else:
            points += 5

        if hdl >= 60:
            points += -1
        elif hdl < 40:
            points += 2
        elif hdl < 50:
            points += 1

        if on_treatment:
            if systolic_bp < 120:
                points += 0
            elif systolic_bp < 130:
                points += 3
            elif systolic_bp < 140:
                points += 4
            elif systolic_bp < 160:
                points += 5
            else:
                points += 6
        else:
            if systolic_bp < 120:
                points += 0
            elif systolic_bp < 130:
                points += 1
            elif systolic_bp < 140:
                points += 2
            elif systolic_bp < 160:
                points += 3
            else:
                points += 4

    # Calcular riesgo a 10 años basado en el total de puntos
    if gender == 'male':
        if points < 0:
            risk = 1
        elif points == 0:
            risk = 1
        elif points == 1:
            risk = 1
        elif points == 2:
            risk = 1
        elif points == 3:
            risk = 1
        elif points == 4:
            risk = 1
        elif points == 5:
            risk = 2
        elif points == 6:
            risk = 2
        elif points == 7:
            risk = 3
        elif points == 8:
            risk = 4
        elif points == 9:
            risk = 5
        elif points == 10:
            risk = 6
        elif points == 11:
            risk = 8
        elif points == 12:
            risk = 10
        elif points == 13:
            risk = 12
        elif points == 14:
            risk = 16
        elif points == 15:
            risk = 20
        elif points == 16:
            risk = 25
        else:
            risk = 30
    else:
        if points < 9:
            risk = 1
        elif points == 9:
            risk = 1
        elif points == 10:
            risk = 1
        elif points == 11:
            risk = 1
        elif points == 12:
            risk = 1
        elif points == 13:
            risk = 2
        elif points == 14:
            risk = 2
        elif points == 15:
            risk = 3
        elif points == 16:
            risk = 4
        elif points == 17:
            risk = 5
        elif points == 18:
            risk = 6
        elif points == 19:
            risk = 8
        elif points == 20:
            risk = 11
        elif points == 21:
            risk = 14
        elif points == 22:
            risk = 17
        elif points == 23:
            risk = 22
        elif points == 24:
            risk = 27
        else:
            risk = 30

    # Clasificación del riesgo y recomendaciones
    if risk < 10:
        risk_level = "bajo"
        recommendation = "Promover hábitos saludables: dieta equilibrada, ejercicio regular y abandono del tabaco. Reevaluar el riesgo cada 4-6 años."
    elif risk < 20:
        risk_level = "moderado"
        recommendation = "Considerar tratamiento farmacológico para hipertensión o dislipemia si está presente. Educación y control estricto de factores de riesgo."
    else:
        risk_level = "alto"
        recommendation = "Indicar prevención secundaria: estatinas, antiagregantes si corresponde, y control estricto de todos los factores de riesgo. Seguimiento regular."

    return risk, risk_level, recommendation
