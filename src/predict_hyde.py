import os
import pandas as pd
import numpy as np 
from tqdm import tqdm
from dotenv import load_dotenv
import argparse
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv(".env")
os.environ['GOOGLE_API_KEY']= os.getenv("GOOGLE_API_KEY") 
from langchain.prompts import ChatPromptTemplate
try:
    from src.cod import get_summarize
    from src.utils import *
    from src.data import Medical_Data
    from src.llm import LLM
    from src.metrics import Metrics
    from src.embedding import Embedding
    from src.search import Searching
except:
    from cod import get_summarize
    from utils import *
    from data import Medical_Data
    from llm import LLM
    from metrics import Metrics
    from embedding import Embedding
    from search import Searching

def hyde_rag(model,question):
    """
    Generate hypothetical answer for the given question
    model: LLM model
    question: str: question
    """
    template_hyde = """Đối với câu hỏi đã cho, hãy thử tạo ra một câu trả lời giả định\
    Chỉ tạo ra câu trả lời và không có gì khác:
    Câu hỏi: {question}
    """
    Prompt = ChatPromptTemplate.from_template(template_hyde)
    query = Prompt.format(question = question)
    hypothetical_answer = model.generate(query)
    return hypothetical_answer
load_dotenv(".env")
def parse_args():
    parser = argparse.ArgumentParser(description="Embedding")
    parser.add_argument("--model_embedding_name", type=str, default="BAAI/bge-m3", help="model name")
    parser.add_argument("--cache_dir", type=str, default="cache/", help="cache directory")
    parser.add_argument("--persist_directory", type=str, default="chroma_db_bge", help="persist directory")
    parser.add_argument("--corpus_path", type=str, default="corpus_summarize", help="corpus path")
    parser.add_argument("--csv_path", type=str, default="data/public_test.csv", help="csv path")
    parser.add_argument("--output_path", type=str, default="submit_hyde.csv", help="output path")
    parser.add_argument("--model_name", type=str, default="google", help="model name")
    parser.add_argument("--k1", type=int, default=3, help="k1")
    parser.add_argument("--k2", type=int, default=3, help="k2")
    return parser.parse_args()
def main():
    args = parse_args()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    corpus_path = args.corpus_path
    docs,texts = load_corpus(corpus_path)
    print("Loaded corpus")
    splits =texts 
    embedding = Embedding(model_name=args.model_embedding_name, cache_dir=args.cache_dir, persist_directory=args.persist_directory,openai_api_key=openai_api_key)
    vectordb = embedding.load_embedding()
    print("Loaded embedding")
    k1 = args.k1
    k2 = args.k2
    search = Searching(k1,k2,vectordb,splits)
    print("Loaded search")
    df = pd.read_csv(args.csv_path)
    result = {"id": [], "answer": []}
    model = LLM(openai_api_key=openai_api_key,google_api_key=google_api_key,model_name =args.model_name)

    print("Loaded model")
    for index, row in tqdm(df.iterrows()):
        result["id"].append(row["id"].strip())
        question, choices, num_choices = process_single_row(row)
        hypothetical_answer = hyde_rag(model,question)
        docs = search.hybrid_search(hypothetical_answer)
        context = search.get_context(docs)
        question = preprocess_question(question)
        prompt = model.preprocess_prompt(question, choices, context)
        answer = model.generate(prompt)
        output_json = process_output(answer, num_choices)
        result["answer"].append(output_json)
    newdf = pd.DataFrame(result, dtype=str)
    newdf.to_csv(args.output_path, index=False)
if __name__ == "__main__":
    #python3 src/predict.py --model_embedding_name="BAAI/bge-m3" --cache_dir="cache/" --persist_directory="chroma_db_bge" --corpus_path="corpus_summarize" --csv_path="data/public_test.csv" --output_path="submit.csv" --corpus_path="corpus_summarize" --model_name="BAAI/bge-m3"
    main()