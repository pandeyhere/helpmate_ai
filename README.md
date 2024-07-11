# HelpMate AI


HelpMate AI
Project Background
The data to query this information for the problem, is not quite there with existing Open AI LLM. We need to train the LLM using RAG (processing existing pdf) and help get the answer for the query.

Problem Statement
Using an external document, figure out the revenue for Uber in 2022.

Create and activate a virtual environment:

```
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

```

Install dependencies:

```
pip3 install -r requirements.txt
```

Set your OpenAI API key as an environment variable:
```
export OPENAI_API_KEY='your_openai_api_key'  # On Windows, use `set OPENAI_API_KEY='your_openai_api_key'`
```

Run the Python App:

```
python3 helpmate.py

```


Give the Input:
```
What is the revenue of uber in 2022?

```
