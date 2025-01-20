import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

from trends_service import TrendsService
from utils import format_timeframe, get_available_countries, prepare_data_for_plot

# Configuration de la page
st.set_page_config(
    page_title="Google Trends Explorer",
    page_icon="📈",
    layout="wide"
)

# Initialisation du service
@st.cache_resource
def get_trends_service():
    return TrendsService()

def main():
    st.title("📈 Google Trends Explorer")

    # Sidebar pour les contrôles
    with st.sidebar:
        st.header("Paramètres")

        # Input pour les mots-clés
        keywords_input = st.text_area(
            "Mots-clés (un par ligne)",
            height=100,
            help="Entrez jusqu'à 5 mots-clés, un par ligne"
        )

        # Sélection du pays
        countries = get_available_countries()
        country = st.selectbox(
            "Pays",
            options=list(countries.keys()),
            format_func=lambda x: countries[x]
        )

        # Sélection de la période
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Date de début",
                value=datetime.now() - timedelta(days=90)
            )
        with col2:
            end_date = st.date_input(
                "Date de fin",
                value=datetime.now()
            )

        # Bouton de recherche
        search_button = st.button("Rechercher", type="primary")

    # Traitement des mots-clés
    keywords = [k.strip() for k in keywords_input.split('\n') if k.strip()]

    if search_button:
        if not keywords:
            st.error("Veuillez entrer au moins un mot-clé")
            return

        if len(keywords) > 5:
            st.warning("Maximum 5 mots-clés autorisés. Seuls les 5 premiers seront utilisés.")
            keywords = keywords[:5]

        try:
            with st.spinner("Récupération des données..."):
                trends_service = get_trends_service()
                timeframe = format_timeframe(start_date, end_date)

                # Récupération des données
                df = trends_service.get_interest_over_time(keywords, country, timeframe)
                df = prepare_data_for_plot(df)

                # Affichage du graphique
                st.subheader("Évolution des tendances")
                fig = px.line(
                    df,
                    x='date',
                    y=keywords,
                    title="Évolution de l'intérêt au fil du temps"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Affichage des données brutes
                with st.expander("Voir les données brutes"):
                    st.dataframe(df)

                # Téléchargement des données
                st.download_button(
                    label="Télécharger les données (CSV)",
                    data=df.to_csv(index=False),
                    file_name="google_trends_data.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"Une erreur est survenue: {str(e)}")

if __name__ == "__main__":
    main()
