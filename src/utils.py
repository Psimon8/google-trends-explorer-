import pandas as pd
from datetime import datetime, timedelta

def format_timeframe(start_date, end_date):
    """Formate les dates pour l'API Google Trends"""
    return f"{start_date.strftime('%Y-%m-%d')} {end_date.strftime('%Y-%m-%d')}"

def get_available_countries():
    """Retourne la liste des pays disponibles"""
    return {
        'FR': 'France',
        'US': 'États-Unis',
        'GB': 'Royaume-Uni',
        'DE': 'Allemagne',
        'ES': 'Espagne',
        'IT': 'Italie',
        'CA': 'Canada',
    }

def prepare_data_for_plot(df):
    """Prépare les données pour la visualisation"""
    df = df.reset_index()
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df
