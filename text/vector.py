from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.document_loaders import TextLoader, UnstructuredFileLoader
#from timm.models.maxxvit import MaxxVitConvCfg
import pinecone 
from dotenv import load_dotenv

load_dotenv()
#loader = TextLoader('../../state_of_the_union.txt')
loader = UnstructuredFileLoader('crisp2003.pdf', "elements")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
# text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()

# initialize pinecone
pinecone.init(
    api_key="7ba866cf-03ba-403e-b7f3-cf83057dcebe",  # find at app.pinecone.io
    environment="us-east-1-aws"  # next to api key in console
)

index_name = "langchain-openai"
namespace = "book"

docsearch = Pinecone.from_texts(
  [doc.page_content for doc in docs], embeddings,
  index_name=index_name, namespace=namespace)

docsearch = Pinecone.from_documents(docs, embeddings, index_name=index_name)

query = "What is the resentment hypothesis?"
docs = docsearch.similarity_search(query)
print(docs[0].page_content)
