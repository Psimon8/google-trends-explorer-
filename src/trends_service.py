from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime, timedelta
import logging

class TrendsService:
    def __init__(self):
        self.pytrends = TrendReq(hl='fr-FR', tz=360)
        self.logger = logging.getLogger(__name__)

    def get_interest_over_time(self, keywords, geo, timeframe):
        """
        Récupère les données de tendances pour les mots-clés spécifiés.

        Args:
            keywords (list): Liste des mots-clés à rechercher
            geo (str): Code pays (ex: 'FR')
            timeframe (str): Période (ex: 'today 12-m')

        Returns:
            pd.DataFrame: DataFrame contenant les données de tendances
        """
        try:
            self.pytrends.build_payload(
                kw_list=keywords[:5],  # Google Trends limite à 5 mots-clés
                cat=0,
                timeframe=timeframe,
                geo=geo
            )

            df = self.pytrends.interest_over_time()
            if df.empty:
                raise ValueError("Aucune donnée trouvée pour ces critères")

            return df

        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des données: {str(e)}")
            raise

    def get_related_queries(self, keyword, geo):
        """
        Récupère les requêtes associées à un mot-clé.
        """
        try:
            self.pytrends.build_payload(
                kw_list=[keyword],
                geo=geo
            )

            related_queries = self.pytrends.related_queries()
            return related_queries[keyword]

        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des requêtes associées: {str(e)}")
            raise
