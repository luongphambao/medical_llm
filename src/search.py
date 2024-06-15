
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
import os 
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
load_dotenv(".env")
openai_api_key = os.getenv('OPENAI_API_KEY')
import ollama
from utils import get_text_from_html_file, get_text_chunks,load_corpus
from embedding import Embedding
model_id ="ontocord/vistral"

class Searching:
    def __init__(self,k1,k2,vectordb,splits):
        self.k1 = k1
        self.k2 = k2
        self.retriever = vectordb.as_retriever(search_kwargs={"k": k1})
        self.bm25_retriever = BM25Retriever.from_documents(splits)
        self.bm25_retriever.k = k2
        self.ensemble_retriever = EnsembleRetriever(retrievers=[self.bm25_retriever, self.retriever], weights=[0.3, 0.7])
    def hybrid_search(self,query):
        ensemble_docs = self.ensemble_retriever.get_relevant_documents(query)
        return ensemble_docs
    def bm25_search(self,query):
        bm25_docs = self.bm25_retriever.get_relevant_documents(query)
        return bm25_docs
    def vector_search(self,query):
        vector_docs = self.retriever.get_relevant_documents(query)
        return vector_docs

corpus_path = 'corpus/'
docs,texts = load_corpus(corpus_path)
print("Loaded corpus")
splits =texts 
embedding = Embedding(model_name="BAAI/bge-m3", device='cpu', cache_dir="cache/", persist_directory="chroma_db_bge")
vectordb = embedding.load_embedding()
print("Loaded embedding")
search = Searching(1,1,vectordb,splits)
print("Loaded search")
query ="Đàn ông có thể bị mắc ung thư vú không?"
vertor_result_docs = search.hybrid_search(query)
print(vertor_result_docs[0].page_content)
#print (f"Your {len(docs)} documents have been split into {len(texts)} chunks")
#embedding = OpenAIEmbeddings(openai_api_key)

# model_name = "BAAI/bge-m3"
# device = 'cuda:0'
# model_kwargs = {'device': device}
# cache_dir = "cache/"
# encode_kwargs = {'normalize_embeddings': True}
# embed_model = SentenceTransformerEmbeddings(
#     model_name=model_name,
#     model_kwargs=model_kwargs,
#     encode_kwargs={'batch_size': 16, "normalize_embeddings": True, "device": device },
#     cache_folder=cache_dir
# )
# # vectordb = Chroma.from_documents(documents=splits, embedding=embed_model,persist_directory="chroma_db_bge")
# # vectordb.persist()
# persist_directory = "chroma_db_bge"
# vectordb = Chroma(persist_directory=persist_directory, embedding_function=embed_model)
# print("Done!")
# query ="Nam đang phải đối mặt với việc phải cắt bỏ một bướu lành tính trên cơ thể mình, anh muốn biết phương pháp cắt bỏ bướu lành tính thường được sử dụng là gì?"
# k=3
# # results = vectordb.similarity_search(query=query, k=k)
# # print(results)
# retriever = vectordb.as_retriever(search_kwargs={"k": 3})
# #retriever.k = k
# bm25_retriever = BM25Retriever.from_documents(splits)
# bm25_retriever.k = 3
# ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, retriever], weights=[0.3, 0.7])

# prompt_template = """Sử dụng các trích đoạn sau đây để trả lời câu hỏi trắc nghiệm (nếu không biết vui lòng trả về không biết.
# {context}
# Câu hỏi: {question}
# Trả lời: """
# import pandas as pd
# import numpy as np

# testset = 'data/public_test.csv'
# df = pd.read_csv(testset)
# ans = pd.DataFrame(columns=['id', 'answer'])

# newline = '\n'
# labels = {0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F'}
# chars = "ABCDEF"
# PROMPT = PromptTemplate(
#     template=prompt_template, input_variables=["context", "question"]
# )
# question_id =0
# list_result=[]
# #llm = ChatOpenAI(temperature=0.1,openai_api_key=openai_api_key)
# query= """Hương đang mang thai tuần thứ 5 và lo lắng mình có thể gặp phải rau tiền đạo. Hương có thể kiểm tra phát hiện bệnh này sau bao nhiêu tuần nữa?
# A. 5 tuần
# B. 15 tuần
# C. 25 tuần
# D. 35 tuần
# """
# ensemble_docs = ensemble_retriever.get_relevant_documents(query)
# # prompt = PROMPT.format_prompt(
# #     context=ensemble_docs,
# #     question=query
# # )
# # result=llm.predict(text=prompt.text)
# # print(result)
# for file in os.listdir("question"):
#     with open("question/"+file, "r", encoding="utf-8") as f:
#         question = f.read()
#         print(question)
#         ensemble_docs = ensemble_retriever.get_relevant_documents(question)
#         prompt = PROMPT.format_prompt(
#             context=ensemble_docs,
#             question=question
#         )
#         result = ollama.generate(model=model_id, prompt=prompt.text).get("response")[0]
#         print(result)
#         #exit()

#         #result=llm.predict(text=prompt.text)
#         list_result.append(result)
#         print(result)
#         print("Câu: ",question_id+1)
#         question_id+=1
#         with open("answers/"+file, "w", encoding="utf-8") as f:
#             f.write(result)
#         #exit()
# # for index, row in df.iterrows():
# #     # if index == 35:
# #     #     break
# #     options = [str(p) for p in row.loc[['option_' + str(i) for i in range(1,7)]] if str(p) != 'nan']
# #     options = [labels[i] + '. ' + p if not p.startswith(f'{labels[i]}.') else p for i, p in enumerate(options)]
# #     #print(options)
# #     len_options = len(options)
# #     question = row.loc['question']
# #     query = f"""{row.loc['question']}
# # {newline.join(options)}
# #     """
# #     #print(query)
# #     ensemble_docs = ensemble_retriever.get_relevant_documents(query)
# #     prompt = PROMPT.format_prompt(
# #         context=ensemble_docs,
# #         question=question
# #     )
# #     #print(prompt.text)
# #     result=llm.predict(text=prompt.text)
# #     print(result)
# #     print(len(options))
# #     print("Câu: ",index+1)
# #     list_result.append(result)
#     #exit()

# # question =""""Nam đang phải đối mặt với việc phải cắt bỏ một bướu lành tính trên cơ thể mình, anh muốn biết phương pháp cắt bỏ bướu lành tính thường được sử dụng là gì?",
# # A. Cắt bỏ bằng dao,
# # B. Cắt bỏ bằng tia laser,
# # C. Cắt bỏ bằng tần số sóng vô tuyến,
# # D. Tất cả đều sai
# # """
# # df['answer_select']=list_result
# # df.to_csv("submission.csv",index=False)
# # prompt = PROMPT.format_prompt(
# #     context=ensemble_docs,
# #     question=question
# # )
# # print(prompt.text)

    

# # result=llm.predict(text=PROMPT.format_prompt(
# #     context=ensemble_docs,
# #     question=query
# # ).text)
# # print(result)