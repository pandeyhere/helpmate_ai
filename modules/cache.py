import pandas as pd
from operator import itemgetter
import chromadb
from modules.parsepdf import process_pdf
import os
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import openai


openai.api_key= os.getenv("OPENAI_API_KEY")


chroma_data_path="data/"
client = chromadb.PersistentClient(path=chroma_data_path)

model = "text-embedding-ada-002"
embedding_function = OpenAIEmbeddingFunction(api_key=openai.api_key, model_name=model)

financedata_collection = client.get_or_create_collection(name='RAG_on_Uber', embedding_function=embedding_function)

cache_collection = client.get_or_create_collection(name='Finance2_Cache', embedding_function=embedding_function)

pdf_path = "data/"


def queryResultsFromCache(query):

    try:
        financedata_collection = process_pdf(embedding_function,client,pdf_path)
        
        cache_results = cache_collection.query(
        query_texts=query,
        n_results=1
        )
        
        # Implementing Cache in Semantic Search

        # Set a threshold for cache search
        threshold = 0.2

        ids = []
        documents = []
        distances = []
        metadatas = []
        results_df = pd.DataFrame()


        # If the distance is greater than the threshold, then return the results from the main collection.

        if cache_results['distances'][0] == [] or cache_results['distances'][0][0] > threshold:
            # Query the collection against the user query and return the top 10 results
            results = financedata_collection.query(
            query_texts=query,
            n_results=10
            )

            for key, val in results.items():
                print(key)

            # Store the query in cache_collection as document w.r.t to ChromaDB so that it can be embedded and searched against later
            # Store retrieved text, ids, distances and metadatas in cache_collection as metadatas, so that they can be fetched easily if a query indeed matches to a query in cache
            Keys = []
            Values = []

            for key, val in results.items():
                if key not in ['embeddings', 'uris','data']:
                    for i in range(10):
                        print(str(val))
                        Keys.append(str(key)+str(i))
                        Values.append(str(val[0][i]))


            cache_collection.add(
                documents= [query],
                ids = [query],  # Or if you want to assign integers as IDs 0,1,2,.., then you can use "len(cache_results['documents'])" as will return the no. of queries currently in the cache and assign the next digit to the new query."
                metadatas = dict(zip(Keys, Values))
            )

            print("Not found in cache. Found in main collection.")

            result_dict = {'Metadatas': results['metadatas'][0], 'Documents': results['documents'][0], 'Distances': results['distances'][0], "IDs":results["ids"][0]}
            results_df = pd.DataFrame.from_dict(result_dict)

            print(results_df)


        # If the distance is, however, less than the threshold, you can return the results from cache

        elif cache_results['distances'][0][0] <= threshold:
            cache_result_dict = cache_results['metadatas'][0][0]

            # Loop through each inner list and then through the dictionary
            for key, value in cache_result_dict.items():
                if 'ids' in key:
                    ids.append(value)
                elif 'documents' in key:
                    documents.append(value)
                elif 'distances' in key:
                    distances.append(value)
                elif 'metadatas' in key:
                    metadatas.append(value)

            print("Found in cache!")

            # Create a DataFrame
            results_df = pd.DataFrame({
                'IDs': ids,
                'Documents': documents,
                'Distances': distances,
                'Metadatas': metadatas
            })

        cache_results = cache_collection.query(
        query_texts=query,
        n_results=1
            )
        
        return results_df
    except Exception as e:
        print(e)
        raise Exception(f"Cache could not be queried.{e.message}")