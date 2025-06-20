
def calcular_bmi(peso_kg, altura_cm):
    altura_m = altura_cm / 100
    bmi = peso_kg / (altura_m ** 2)
    categoria = ""
    if bmi < 18.5:
        categoria = "Bajo peso"
    elif 18.5 <= bmi < 25:
        categoria = "Normal"
    elif 25 <= bmi < 30:
        categoria = "Sobrepeso"
    else:
        categoria = "Obesidad"
    return round(bmi, 1), categoria
