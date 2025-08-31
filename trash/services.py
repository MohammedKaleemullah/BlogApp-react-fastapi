"""All services in one file."""

import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import text
from pinecone import Pinecone, ServerlessSpec
from google import genai
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

class ServiceManager:
    """Manages all services in one class."""
    
    def __init__(self):
        # Database
        self.db_engine = None
        
        # Pinecone
        self.pinecone_client = None
        self.index_name = "simple-rag"
        
        # Gemini
        self.gemini_client = None
        
    def initialize_all(self) -> bool:
        """Initialize all services."""
        try:
            # Database
            db_url = f"postgresql+psycopg2://{os.getenv('db_user')}:{os.getenv('db_password')}@{os.getenv('db_host')}:{os.getenv('db_port')}/{os.getenv('db_database')}"
            self.db_engine = sqlalchemy.create_engine(db_url)
            
            # Test database
            with self.db_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database connected")
            
            # Pinecone
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            existing_indexes = [index.name for index in pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                pc.create_index(
                    name=self.index_name,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")
                )
                print(f"✅ Created Pinecone index: {self.index_name}")
            else:
                print(f"✅ Pinecone index exists: {self.index_name}")
                
            self.pinecone_client = pc
            
            # Gemini
            self.gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            
            # Test Gemini
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents="Say 'OK'"
            )
            print("✅ Gemini connected")
            
            return True
            
        except Exception as e:
            print(f"❌ Service initialization failed: {e}")
            return False
    
    def test_database(self) -> bool:
        """Test database connection."""
        try:
            with self.db_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except:
            return False
    
    def test_pinecone(self) -> bool:
        """Test Pinecone connection."""
        try:
            self.pinecone_client.Index(self.index_name).describe_index_stats()
            return True
        except:
            return False
    
    def test_gemini(self) -> bool:
        """Test Gemini connection."""
        try:
            self.gemini_client.models.generate_content(
                model="gemini-2.5-flash", 
                contents="test"
            )
            return True
        except:
            return False
    
    def fetch_blogs(self, limit: int = 50):
        """Fetch blogs from database."""
        with self.db_engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, title, content FROM blogapp_schema.blog LIMIT :limit"),
                {"limit": limit}
            )
            return [
                {"id": row[0], "title": row[1], "content": row[2] or ""}
                for row in result.fetchall()
            ]
    
    def embed_text(self, text: str):
        """Generate embedding for text."""
        response = self.gemini_client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        return response.embeddings[0].values
    
    def chunk_text(self, text: str, chunk_size: int = 1000):
        """Split text into chunks."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=200
        )
        return splitter.split_text(text)
    
    def index_blogs(self, limit: int = 50, chunk_size: int = 1000):
        """Index blogs into Pinecone."""
        # Fetch blogs
        blogs = self.fetch_blogs(limit)
        
        # Create chunks and vectors
        vectors = []
        chunks_count = 0
        
        for blog in blogs:
            if not blog["content"]:
                continue
                
            chunks = self.chunk_text(blog["content"], chunk_size)
            
            for i, chunk in enumerate(chunks):
                embedding = self.embed_text(chunk)
                vectors.append({
                    "id": f"{blog['id']}_{i}",
                    "values": embedding,
                    "metadata": {"text": chunk}
                })
                chunks_count += 1
        
        # Upsert to Pinecone
        if vectors:
            index = self.pinecone_client.Index(self.index_name)
            
            # Batch upsert
            batch_size = 50
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                index.upsert(vectors=batch)
        
        return {
            "blogs_count": len(blogs),
            "chunks_count": chunks_count
        }
    
    def process_query(self, query: str, top_k: int = 3):
        """Process a RAG query."""
        # Get query embedding
        query_embedding = self.embed_text(query)
        
        # Search Pinecone
        index = self.pinecone_client.Index(self.index_name)
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Get relevant chunks
        chunks = [match["metadata"]["text"] for match in results["matches"]]
        
        if not chunks:
            return "No relevant information found."
        
        # Generate answer
        context = "\n\n".join(chunks)
        prompt = f"""Answer the question based on this content:

{context}

Question: {query}
Answer:"""
        
        response = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"temperature": 0.2, "max_output_tokens": 1024}
        )
        
        return response.candidates[0].content.parts[0].text
    
    def cleanup(self):
        """Cleanup resources."""
        if self.db_engine:
            self.db_engine.dispose()
        print("✅ Services cleaned up")
