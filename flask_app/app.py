
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
from utils import search_articles, generate_answer, create_conversational_system, fetch_article_content

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Global conversation chain to maintain context
global_conversation_chain = None
# Modify the Flask route to reset the conversation chain for each query
@app.route('/query', methods=['POST'])
def query():
    global global_conversation_chain
    
    try:
        # Get the data/query from the request
        data = request.get_json()
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({"error": "No query provided"}), 400
        
        # Reset the global conversation chain for each new query
        global_conversation_chain = None
        
        # Step 1: Search and scrape articles based on the query
        print(f"Searching for query: {user_query}")
        articles = search_articles(user_query)
        
        # Check if articles list is empty
        if not articles:
            return jsonify({
                'answer': "I couldn't find any relevant sources for this query.",
                'sources': []
            })
        
        # Step 2: Fetch content from top articles
        print(f"Found {len(articles)} articles. Fetching contents...")
        contents = []
        for article in articles:
            content = fetch_article_content(article['url'])
            print(f"Article {article['url']}: Content length = {len(content)}")
            if content:
                contents.append(content)
        
        # Check if no valid contents were found
        if not contents:
            return jsonify({
                'answer': "I couldn't extract meaningful content from the sources.",
                'sources': [article['url'] for article in articles]
            })
        
        concatenated_content = ' '.join(contents)
        
        # Step 3: Generate an answer using the LLM
        print("Generating answer...")
        # Create a new conversation chain for each query
        conversation_chain = create_conversational_system(concatenated_content)
        
        answer = generate_answer(
            concatenated_content, 
            user_query, 
            conversation_chain
        )
        
        return jsonify({
            'answer': answer,
            'sources': [article['url'] for article in articles]
        })
    
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=5001, debug=True)