from langchain_pinecone import PineconeVectorStore
from langchain_cohere import CohereEmbeddings
from ..config import Settings


class KnowledgeBaseService:
    def __init__(self):
        self.index_name = Settings.PINECONE_INDEX
        self.vectorstore = None
        self.embeddings = CohereEmbeddings(model=Settings.COHERE_MODEL)

    def search(self, query: str, k: int = 3) -> str:
        if not self.vectorstore:
            self.vectorstore = PineconeVectorStore.from_existing_index(
                self.index_name, self.embeddings
            )
        
        docs = self.vectorstore.similarity_search(query, k=k)
        return "\n\n".join([doc.page_content for doc in docs])
