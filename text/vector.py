
import os
from dotenv import load_dotenv
load_dotenv()

def pinecone_run():
  from langchain.embeddings.openai import OpenAIEmbeddings
  from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
  from langchain.vectorstores import Pinecone
  from langchain.document_loaders import TextLoader, UnstructuredFileLoader
  #from timm.models.maxxvit import MaxxVitConvCfg
  import pinecone 


  #loader = TextLoader('../../state_of_the_union.txt')
  loader = UnstructuredFileLoader('crisp2003.pdf', "elements")
  documents = loader.load()
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
  # text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
  docs = text_splitter.split_documents(documents)

  embeddings = OpenAIEmbeddings()

  # initialize pinecone
  pinecone.init(
      api_key=os.getenv("PINECONE_API_KEY"),  # find at app.pinecone.io
      environment=os.getenv("us-east-1-aws")# next to api key in console
  )

  index_name = "langchain-openai"
  namespace = "book"

  docsearch = Pinecone.from_texts(
  [doc.page_content for doc in docs], embeddings,
  index_name=index_name, namespace=namespace)
  query = "What is the resentment hypothesis?"

  '''
  docsearch = Pinecone.from_documents(docs, embeddings, index_name=index_name)

  docs = docsearch.similarity_search(query)
  print(docs[0].page_content)
  '''

  from langchain.llms import OpenAI
  from langchain.chains.question_answering import load_qa_chain
  import os

  llm = OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
  chain = load_qa_chain(llm, chain_type="stuff")

  docs = docsearch.similarity_search(query,
  include_metadata=True, namespace=namespace)

  chain.run(input_documents=docs, question=query)

def chroma_run():
  import chromadb
  from langchain.vectorstores import Chroma
  from langchain.embeddings.openai import OpenAIEmbeddings

  embeddings = OpenAIEmbeddings()
  vectorstore = Chroma("langchain_store", embeddings.embed_query)


  chroma_client = chromadb.Client()
  collection = chroma_client.create_collection(name="my_collection") # Collections are where you'll store your embeddings, documents, and any additional metadata. You can create a collection with a name:
  collection.add(
    documents=["This is a document", "This is another document"],
    metadatas=[{"source": "my_source"}, {"source": "my_source"}],
    ids=["id1", "id2"]
  )
  results = collection.query(
    query_texts=["This is a query document"],
    n_results=2
  )

if __name__ == "__main__":
  pinecone_run()