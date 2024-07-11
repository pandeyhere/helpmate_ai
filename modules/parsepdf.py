import pdfplumber
from pathlib import Path
import pandas as pd
from operator import itemgetter
import json
import json

import pandas as pd
import json



def process_pdf(embedding_function,client, pdf_path):
    try:
        # Define the directory containing the PDF files
        pdf_directory = Path(pdf_path)

        # Initialize an empty list to store the extracted texts and document names
        data = []

        # Loop through all files in the directory
        for pdf_path in pdf_directory.glob("*.pdf"):

            # Process the PDF file
            print(f"...Processing {pdf_path.name}")

            # Call the function to extract the text from the PDF
            extracted_text = extract_text_from_pdf(pdf_path)

            # Convert the extracted list to a PDF, and add a column to store document names
            extracted_text_df = pd.DataFrame(extracted_text, columns=['Page No.', 'Page_Text'])
            extracted_text_df['Document Name'] = pdf_path.name

            # Append the extracted text and document name to the list
            data.append(extracted_text_df)

            # Print a message to indicate progress
            print(f"Finished processing {pdf_path.name}")

        # Print a message to indicate all PDFs have been processed
        print("All PDFs have been processed.")

        finance_pdfs_data = pd.concat(data, ignore_index=True)

        finance_pdfs_data['Metadata'] = finance_pdfs_data.apply(lambda x: {'filing_name': x['Document Name'][:-4], 'Page_No.': x['Page No.']}, axis=1)

        print(finance_pdfs_data.head(5))

        financedata_collection = client.get_or_create_collection(name='RAG_on_Uber', embedding_function=embedding_function)

        documents_list = finance_pdfs_data["Page_Text"].tolist()
        metadata_list = finance_pdfs_data['Metadata'].tolist()


        financedata_collection.add(
            documents= documents_list,
            ids = [str(i) for i in range(0, len(documents_list))],
            metadatas = metadata_list
        )

        return financedata_collection
    except Exception as e:
        print(e)
        raise Exception(f"Document could not be parsed.{e.message}")



def extract_text_from_pdf(pdf_path):
    try:
        p = 0
        full_text = []


        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_no = f"Page {p+1}"
                text = page.extract_text()

                tables = page.find_tables()
                table_bboxes = [i.bbox for i in tables]
                tables = [{'table': i.extract(), 'top': i.bbox[1]} for i in tables]
                non_table_words = [word for word in page.extract_words() if not any(
                    [check_bboxes(word, table_bbox) for table_bbox in table_bboxes])]
                lines = []

                for cluster in pdfplumber.utils.cluster_objects(non_table_words + tables, itemgetter('top'), tolerance=5):

                    if 'text' in cluster[0]:
                        try:
                            lines.append(' '.join([i['text'] for i in cluster]))
                        except KeyError:
                            pass

                    elif 'table' in cluster[0]:
                        lines.append(json.dumps(cluster[0]['table']))


                full_text.append([page_no, " ".join(lines)])
                p +=1

        return full_text
    except Exception as e:
        print(e)
        raise Exception(f"Text could not be extracted from PDF.{e.message}")


def check_bboxes(word, table_bbox):
    # Check whether word is inside a table bbox.
    l = word['x0'], word['top'], word['x1'], word['bottom']
    r = table_bbox
    return l[0] > r[0] and l[1] > r[1] and l[2] < r[2] and l[3] < r[3]
