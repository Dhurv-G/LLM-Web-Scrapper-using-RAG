import os
import requests
import json 
from bs4 import BeautifulSoup
import google.generativeai as genai
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import GooglePalmEmbeddings

# Load API keys from environment variables
from dotenv import load_dotenv
load_dotenv()
# Load API keys from environment variables
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY) 

def search_articles(query):
    """
    Enhanced search strategy with multiple search types
    """
    search_types = [
        {"type": "search", "num": 5},     # Web search
        {"type": "news", "num": 3},       # News articles
        {"type": "images", "num": 2}      # Image context might help
    ]
    
    all_results = []
    
    for search_config in search_types:
        payload = json.dumps({
            "q": query,
            "num": search_config['num'],
            "type": search_config['type']
        })
        
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                "https://google.serper.dev/search", 
                headers=headers, 
                data=payload
            )
            
            if response.status_code == 200:
                results = response.json().get('organic', [])
                print(f"Search type {search_config['type']} results: {len(results)}")  # Debug print
                all_results.extend([
                    {"url": result['link'], "title": result['title']} 
                    for result in results 
                    if result.get('link')
                ])
        
        except Exception as e:
            print(f"Search error for {search_config['type']}: {e}")
    
    # Remove duplicates while preserving order
    unique_results = []
    seen = set()
    for result in all_results:
        if result['url'] not in seen:
            unique_results.append(result)
            seen.add(result['url'])
    
    # Add a print to check the final results
    print(f"Total unique results: {len(unique_results)}")
    
    return unique_results[:7]  # Limit to 7 unique sources

def fetch_article_content(url):
    """
    Advanced content extraction with multiple strategies
    """
    try:
        # Skip problematic domains
        skip_domains = [
            'youtube.com', 'twitter.com', 'facebook.com', 
            'instagram.com', 'pinterest.com'
        ]
        if any(domain in url for domain in skip_domains):
            return ""

        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })
        
        # Check response
        if response.status_code != 200:
            print(f"Failed to fetch {url}: HTTP {response.status_code}")
            return ""

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unnecessary elements
        for script in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe', 'form', 'comment']):
            script.decompose()

        # Advanced content extraction strategies
        content_strategies = [
            # Strategy 1: Specific content tags for different site types
            lambda: ' '.join([
                part.get_text(strip=True) 
                for part in soup.find_all(['article', 'main', 'div.content', 'div.article-body', 
                                           'div.entry-content', 'section.content'])
                if part
            ]),
            
            # Strategy 2: Paragraphs and headings with more comprehensive selection
            lambda: ' '.join([
                part.get_text(strip=True) 
                for part in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4'])
                if part and len(part.get_text(strip=True)) > 50
            ]),
            
            # Strategy 3: Extended text extraction
            lambda: soup.get_text(separator=' ', strip=True)
        ]
        
        # Try strategies until we get meaningful content
        for strategy in content_strategies:
            content = strategy()
            
            # More robust content validation
            if content and len(content) > 200:
                # Basic keyword relevance check
                return content[:7000]  # Limit content length
        
        return ""
    
    except requests.RequestException as e:
        print(f"Request error for {url}: {e}")
        return ""
    except Exception as e:
        print(f"Content extraction error for {url}: {e}")
        return ""

# Change this part in the create_conversational_system function
def create_conversational_system(initial_context):
    """
    Create a conversational retrieval system using Langchain and Google Generative AI
    """
    # Initialize Google's Generative AI
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-latest", 
        google_api_key=GOOGLE_API_KEY, 
        temperature=0.7
    )
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    texts = text_splitter.split_text(initial_context)
    
    # Update the embeddings - use Google's embedding model
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GOOGLE_API_KEY
    )
    
    vectorstore = FAISS.from_texts(texts, embeddings)
    
    # Rest of the function remains the same
    memory = ConversationBufferMemory(
        memory_key="chat_history", 
        return_messages=True
    )
    
    conversational_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        verbose=True
    )
    
    return conversational_chain

def generate_answer(content, query, conversation_chain):
    """
    Enhanced answer generation with context and instructions
    """
    # Craft a more specific prompt
    enhanced_prompt = f"""
    Context: {content[:5000]}

    Specific Query: {query}

    Instructions:
    1. Provide a clear, concise answer directly related to the query
    2. If the context doesn't contain enough information, state that clearly
    3. Focus on delivering the most relevant information
    4. Use a neutral, informative tone
    5. If no relevant information is found, acknowledge the lack of information
    """
    
    try:
        response = conversation_chain({"question": enhanced_prompt})
        answer = response.get('answer', "I couldn't find definitive information about this query.")
        
        # Additional check to ensure the answer is relevant
        if len(answer.strip()) < 10 or "does not contain" in answer.lower():
            return "I couldn't find specific information about this query in the available sources."
        
        return answer
    
    except Exception as e:
        print(f"Answer generation error: {e}")
        return "I encountered an issue generating a response. Please try again."