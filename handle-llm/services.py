import os
import time
import sqlalchemy
from sqlalchemy import text
from pinecone import Pinecone, ServerlessSpec
from google import genai as genai_client
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import get_database_url

class ServiceManager:
    def __init__(self):
        self.db_engine = None
        self.pinecone_client = None
        self.index_name = "rag-index-v1"
        self.gemini_client = None
        self.services_initialized = False
        self.index_populated = False
        
    def initialize_all(self) -> bool:
        print("🚀 Starting service initialization...")
        
        try:
            # Database
            print("🔗 Connecting to database...")
            self.db_engine = sqlalchemy.create_engine(get_database_url())
            with self.db_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database connected")
            
            # Pinecone
            print("🔗 Connecting to Pinecone...")
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            existing_indexes = [index.name for index in pc.list_indexes()]

            index_created = False
            if self.index_name not in existing_indexes:
                print(f"Creating new Pinecone index: {self.index_name}")
                pc.create_index(
                    name=self.index_name,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")
                )
                print(f"✅ Created Pinecone index: {self.index_name}")
                index_created = True
                time.sleep(10)
            else:
                print(f"✅ Pinecone index exists: {self.index_name}")
                
            self.pinecone_client = pc
            
            # Gemini for RAG
            print("🔗 Connecting to Gemini...")
            self.gemini_client = genai_client.Client(api_key=os.getenv("GEMINI_API_KEY"))
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash", contents="Say 'OK'"
            )
            print("✅ Gemini connected")
            
            self.services_initialized = True
            
            # Auto-index blogs
            if index_created or not self.is_index_populated():
                print("🔄 Auto-indexing blogs during startup...")
                try:
                    result = self.index_blogs(limit=20, chunk_size=1000)
                    print(f"✅ Auto-indexed {result['blogs_count']} blogs with {result['chunks_count']} chunks")
                    self.index_populated = True
                except Exception as e:
                    print(f"⚠️ Auto-indexing failed: {e}")
            else:
                print("✅ Index already has data, skipping auto-indexing")
                self.index_populated = True
            
            print("🎉 All services initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Service initialization failed: {e}")
            self.services_initialized = False
            return False
    
    def is_index_populated(self) -> bool:
        """Check if the Pinecone index has data."""
        try:
            index = self.pinecone_client.Index(self.index_name)
            stats = index.describe_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            print(f"📊 Index has {total_vectors} vectors")
            return total_vectors > 0
        except Exception as e:
            print(f"⚠️ Could not check index stats: {e}")
            return False
    
    def test_database(self) -> bool:
        if not self.db_engine:
            return False
        try:
            with self.db_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except:
            return False
    
    def test_pinecone(self) -> bool:
        if not self.pinecone_client:
            return False
        try:
            self.pinecone_client.Index(self.index_name).describe_index_stats()
            return True
        except:
            return False
    
    def test_gemini(self) -> bool:
        if not self.gemini_client:
            return False
        try:
            self.gemini_client.models.generate_content(
                model="gemini-2.5-flash", contents="test"
            )
            return True
        except:
            return False
    
    def fetch_blogs(self, limit: int = 50):
        """Fetch blogs from database."""
        if not self.db_engine:
            raise RuntimeError("Database not connected")
            
        with self.db_engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, title, content FROM blogapp_schema.blog WHERE content IS NOT NULL AND content != '' LIMIT :limit"),
                {"limit": limit}
            )
            blogs = [
                {"id": row[0], "title": row[1], "content": row[2]}
                for row in result.fetchall()
                if row[2] and len(row[2].strip()) > 50
            ]
            print(f"📚 Fetched {len(blogs)} blogs with content")
            return blogs
    
    def embed_text(self, text: str):
        """Generate embedding for text."""
        if not self.gemini_client:
            raise RuntimeError("Gemini client not connected")
            
        clean_text = text.strip()[:8000]
        response = self.gemini_client.models.embed_content(
            model="text-embedding-004", contents=clean_text
        )
        return response.embeddings[0].values
    
    def chunk_text(self, text: str, chunk_size: int = 1000):
        """Split text into chunks."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=200
        )
        return splitter.split_text(text)
    
    def index_blogs(self, limit: int = 50, chunk_size: int = 1000):
        """Index blogs into Pinecone."""
        if not self.services_initialized:
            raise RuntimeError("Services not initialized")
            
        print(f"🔄 Starting indexing process for {limit} blogs...")
        blogs = self.fetch_blogs(limit)
        
        if not blogs:
            print("⚠️ No blogs found with content to index")
            return {"blogs_count": 0, "chunks_count": 0}
        
        vectors = []
        chunks_count = 0
        
        for blog in blogs:
            if not blog["content"] or len(blog["content"].strip()) < 50:
                continue
                
            print(f"📝 Processing blog {blog['id']}: {blog['title'][:50]}...")
            full_content = f"Title: {blog['title']}\n\nContent: {blog['content']}"
            chunks = self.chunk_text(full_content, chunk_size)
            
            for i, chunk in enumerate(chunks):
                try:
                    embedding = self.embed_text(chunk)
                    vectors.append({
                        "id": f"blog_{blog['id']}_chunk_{i}",
                        "values": embedding,
                        "metadata": {
                            "text": chunk,
                            "blog_id": str(blog['id']),
                            "blog_title": blog['title'],
                            "chunk_index": i
                        }
                    })
                    chunks_count += 1
                    
                    if len(vectors) % 10 == 0:
                        print(f"  📊 Processed {len(vectors)} chunks...")
                        
                except Exception as e:
                    print(f"⚠️ Failed to embed chunk {i} from blog {blog['id']}: {e}")
                    continue
        
        # Upsert to Pinecone
        if vectors:
            print(f"🚀 Upserting {len(vectors)} vectors to Pinecone...")
            index = self.pinecone_client.Index(self.index_name)
            
            batch_size = 50
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                try:
                    index.upsert(vectors=batch)
                    print(f"  ✅ Upserted batch {i//batch_size + 1}/{(len(vectors) + batch_size - 1)//batch_size}")
                except Exception as e:
                    print(f"⚠️ Failed to upsert batch {i//batch_size + 1}: {e}")
            
            time.sleep(2)
            stats = index.describe_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            print(f"📊 Index now has {total_vectors} total vectors")
        
        result = {"blogs_count": len(blogs), "chunks_count": chunks_count}
        print(f"✅ Indexing completed: {result}")
        return result
    
    def process_query(self, query: str, top_k: int = 3):
        """Process a RAG query with friendly system prompt."""
        if not self.services_initialized:
            raise RuntimeError("Services not initialized")
        
        print(f"🔍 Processing query: '{query}'")
        
        if not self.is_index_populated():
            return """I don't have any blog content indexed yet!
            Please index some blogs first so I can help you find information."""
        
        # Get query embedding and search
        query_embedding = self.embed_text(query)
        index = self.pinecone_client.Index(self.index_name)
        results = index.query(
            vector=query_embedding, top_k=top_k, include_metadata=True
        )
        
        print(f"📊 Found {len(results.get('matches', []))} matches")
        
        chunks = []
        for match in results.get('matches', []):
            if match.get('score', 0) > 0.1:
                chunks.append(match["metadata"]["text"])
        
        if not chunks:
            return f"""I couldn't find specific information about "{query}" in our blog database."""
        with open("system_prompt.txt", "r", encoding="utf-8") as f:
            system_prompt = f.read()
        context = "\n\n".join(chunks)
        user_prompt = f"""BLOG CONTENT:
{context}

USER QUESTION: {query}

Provide a comprehensive analysis based solely on the blog content above. 
If information is limited, clearly indicate what additional details would be helpful."""

        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
            config={"temperature": 0.2, "max_output_tokens": 2048}
        )
        
        if (response and response.candidates and 
            response.candidates[0].content and
            response.candidates[0].content.parts):
            return response.candidates[0].content.parts[0].text
        else:
            return "I'm having trouble generating a response right now. Please try again!!!"
    
    def cleanup(self):
        """Cleanup resources."""
        if self.db_engine:
            self.db_engine.dispose()
        print("✅ Services cleaned up")
