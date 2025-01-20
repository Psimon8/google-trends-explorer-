from pytrends.request import TrendReq
import pandas as pd
import time
from datetime import datetime, timedelta
import logging
import streamlit as st
import json
import hashlib

class TrendsService:
    def __init__(self):
        self.pytrends = TrendReq(hl='fr-FR', 
                                tz=360,
                                timeout=(10,25),  # Augmente le timeout
                                retries=2,
                                backoff_factor=0.1)
        self.logger = logging.getLogger(__name__)
        
    @st.cache_data(ttl=3600)  # Cache les résultats pendant 1 heure
    def get_interest_over_time(self, keywords, geo, timeframe):
        """
        Récupère les données de tendances avec gestion du cache et des erreurs
        """
        # Création d'une clé unique pour le cache
        cache_key = self._create_cache_key(keywords, geo, timeframe)
        
        try:
            # Attente entre les requêtes pour éviter le rate limiting
            time.sleep(1)  
            
            self.pytrends.build_payload(
                kw_list=keywords[:5],
                cat=0,
                timeframe=timeframe,
                geo=geo
            )
            
            # Nouvelle tentative avec backoff exponentiel
            for attempt in range(3):
                try:
                    df = self.pytrends.interest_over_time()
                    if not df.empty:
                        return df
                except Exception as e:
                    if attempt == 2:  # Dernière tentative
                        raise
                    wait_time = (2 ** attempt) * 2  # 2, 4, 8 secondes
                    time.sleep(wait_time)
            
            if df.empty:
                raise ValueError("Aucune donnée trouvée pour ces critères")
                
            return df
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                raise Exception(
                    "Limite de requêtes atteinte. Veuillez attendre quelques minutes avant de réessayer."
                )
            self.logger.error(f"Erreur lors de la récupération des données: {error_msg}")
            raise

    def _create_cache_key(self, keywords, geo, timeframe):
        """Crée une clé unique pour le cache"""
        cache_str = f"{'-'.join(sorted(keywords))}_{geo}_{timeframe}"
        return hashlib.md5(cache_str.encode()).hexdigest()

    def get_related_queries(self, keyword, geo):
        """Récupère les requêtes associées avec gestion du cache"""
        @st.cache_data(ttl=3600)
        def _fetch_related_queries(kw, geo):
            time.sleep(1)  # Pause pour éviter le rate limiting
            self.pytrends.build_payload(
                kw_list=[kw],
                geo=geo
            )
            return self.pytrends.related_queries()

        try:
            related_queries = _fetch_related_queries(keyword, geo)
            return related_queries.get(keyword, {})
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des requêtes associées: {str(e)}")
            raise
