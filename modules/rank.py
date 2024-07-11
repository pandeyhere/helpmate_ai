import pdfplumber
from pathlib import Path
import pandas as pd
from operator import itemgetter
import json
import tiktoken
import chromadb
import openai
import json, os, ast
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from modules.cache import queryResultsFromCache

import openai
import pandas as pd
import json, os, ast

from tenacity import retry, wait_random_exponential, stop_after_attempt
from sentence_transformers import CrossEncoder, util

def get_top_3_documents_by_rank(query,results_df):
    try:
        cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
        cross_inputs = [[query, response] for response in results_df['Documents']]
        cross_rerank_scores = cross_encoder.predict(cross_inputs)
        
        results_df['Reranked_scores'] = cross_rerank_scores
        
        top_3_semantic = results_df.sort_values(by='Distances')
        top_3_semantic[:3]
        
        top_3_rerank = results_df.sort_values(by='Reranked_scores', ascending=False)
        top_3_rerank[:3]
        top_3_RAG = top_3_rerank[["Documents", "Metadatas"]][:3]
        retrieved = list(top_3_RAG['Documents'][:3])

        return retrieved
    except Exception as e:
        print(e)
        raise Exception(f"Ranking could not be determined.{e.message}")