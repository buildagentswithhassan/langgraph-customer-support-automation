from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_cohere import CohereEmbeddings


class KnowledgeBase:
    def __init__(self, pdf_path: str, index_name: str = "support-kb"):
        self.pdf_path = pdf_path
        self.index_name = index_name
        self.vectorstore = None
        self.embeddings = CohereEmbeddings(model="embed-english-light-v3.0")

    def load_and_index(self):
        """Load PDF and create Pinecone vector index"""
        loader = PyPDFLoader(self.pdf_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)

        self.vectorstore = PineconeVectorStore.from_documents(
            splits, self.embeddings, index_name=self.index_name
        )


# Global instance
kb = KnowledgeBase("../resources/CompanySupportPolicyandKnowledgeBase.pdf")
