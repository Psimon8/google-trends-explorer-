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
        self.pytrends = TrendReq(hl='fr-FR', tz=360)
        self.logger = logging.getLogger(__name__)

    def get_interest_over_time(self, keywords, geo, timeframe):
        """
        Fetch interest over time with rate-limiting and retry logic.
        """
        try:
            # Build the payload
            self.pytrends.build_payload(
                kw_list=keywords[:5],  # Google Trends allows up to 5 keywords
                cat=0,
                timeframe=timeframe,
                geo=geo
            )

            # Retry logic with exponential backoff
            for attempt in range(3):  # Retry up to 3 times
                try:
                    time.sleep(2 ** attempt)  # Exponential backoff: 2, 4, 8 seconds
                    data = self.pytrends.interest_over_time()
                    if not data.empty:
                        return data
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        raise
                    self.logger.warning(f"Retrying due to error: {e}")

            raise Exception("Failed to fetch data after multiple attempts.")

        except Exception as e:
            if "429" in str(e):
                raise Exception(
                    "Rate limit exceeded. Please wait a few minutes before retrying."
                )
            self.logger.error(f"Error fetching data: {e}")
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
