"""Independent HAS-BLED screen; arithmetic lives in calculations.py."""
from clinical_ui import render_score


def calcular(t):
    return render_score('has_bled', t)
