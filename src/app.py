import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import time
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
            "Mots-clés (un par ligne, max 5)",
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

        # Sélection de la période avec limitations
        col1, col2 = st.columns(2)
        with col1:
            min_date = datetime.now() - timedelta(days=365)  # Limite à 1 an
            start_date = st.date_input(
                "Date de début",
                value=datetime.now() - timedelta(days=90),
                min_value=min_date,
                max_value=datetime.now()
            )
        with col2:
            end_date = st.date_input(
                "Date de fin",
                value=datetime.now(),
                min_value=start_date,
                max_value=datetime.now()
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

                # Récupération des données avec gestion du cache
                df = trends_service.get_interest_over_time(keywords, country, timeframe)

                if df is not None and not df.empty:
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
                else:
                    st.warning("Aucune donnée disponible pour ces critères")

        except Exception as e:
            st.error(f"Une erreur est survenue: {str(e)}")
            if "429" in str(e):
                st.info("Conseil: Attendez quelques minutes avant de réessayer. "
                       "Google Trends limite le nombre de requêtes par période.")

if __name__ == "__main__":
    main()
