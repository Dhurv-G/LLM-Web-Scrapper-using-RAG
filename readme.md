# **LLM-Based RAG System**

## **Overview**

This project implements a Retrieval-Augmented Generation (RAG) system using a Large Language Model (LLM). The system integrates with APIs to scrape content from the web and uses a separate API to serve LLM-generated answers. It features a Streamlit-based front-end interface for user interaction and a Flask backend for processing.

**Note:** Only use the packages listed in the `requirements.txt` file. Similar or alternative packages are acceptable if they perform equivalent functions.

---

## **Process Overview**

1. **User Input via Streamlit Interface**:
   - The user enters a query through the Streamlit front-end.

2. **Query Sent to Flask Backend**:
   - The user’s query is sent to the Flask backend via an API call for processing.

3. **Internet Search and Article Scraping**:
   - The Flask backend performs an internet search using an API.
   - It retrieves the most relevant articles and scrapes their content (e.g., headings and paragraphs).

4. **Content Processing**:
   - The scraped content is pre-processed to form coherent input for the LLM.

5. **LLM Response Generation**:
   - The processed content, combined with the user’s query, is sent to an LLM API.
   - The LLM generates a contextual response and sends it back to the Flask backend.

6. **Response Sent Back to Streamlit Interface**:
   - The Flask backend returns the response, which is displayed in the Streamlit front-end.

**Bonus Feature**: Use LangChain or similar tools to add memory and enhance conversational abilities.

---

## **Prerequisites**

- Python 3.8 or above
- API keys for internet search and LLM services

---

## **Setup Instructions**

### Step 1: Clone or download the Repository (if emailed)

```bash
git clone https://github.com/Dhurv-G/LLM-Web-Scrapper-using-RAG.git
cd LLM-Web-Scrapper-using-RAG
```

Or download it

### Step 2: Set Up a Virtual Environment

You can use `venv` or `conda` to create an isolated environment for this project.

#### Using `venv`

```bash
python -m venv env
source env/bin/activate  # On Windows, use `env\Scripts\activate`
```

#### Using `conda`

```bash
conda create --name project_env python=3.8
conda activate project_env
```

### Step 3: Install Requirements

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the root directory.  
Add your API keys and any other sensitive data as follows:

```plaintext
FLASK_API_KEY=your_flask_api_key
LLM_API_KEY=your_llm_api_key
```


### Step 5: Run the Flask Backend

Navigate to the `flask_app` directory and start the Flask server:

```bash
cd flask_app
python app.py
```

### Step 6: Run the Streamlit Frontend

In a new terminal, run the Streamlit app:

```bash
cd streamlit_app
streamlit run app.py
```

### Step 7: Open the Application

Open your web browser and go to `http://localhost:8501`. You can now interact with the system by entering your query.

## **Project Structure** 

```plaintext
LLM-Web-Scrapper-using-RAG/
├── flask_app/
│   ├── app.py           # Flask backend
│   └── utils.py         # Utility functions for processing
├── streamlit_app/
│   ├── app.py           # Streamlit front-end
│   └── utils.py         # Utility functions for front-end
├── .env                 # Environment variables (not included in version control)
├── requirements.txt     # Project dependencies
└── README.md            # Documentation
```
- **flask_app/**: Contains the backend Flask API and utility functions.
- **streamlit_app/**: Contains the Streamlit front-end code.
- **.env**: Stores API keys (make sure this file is not included in version control).
- **requirements.txt**: Lists the project dependencies.

## **Future Enhancements**

- **Enable Multi-Language Support**: Expand the system to support multiple languages for both input queries and responses.
- **Advanced Search Integration**: Include additional data sources (e.g., Google Scholar, PubMed, or specific APIs) for retrieving more diverse and authoritative content.
- **Scalability with Cloud Services**: Migrate the system to cloud-based platforms like AWS or GCP for better scalability and performance during high traffic.
- **Feedback and Learning Mechanism**: Implement a feedback loop for users to rate the responses, enabling continuous improvement of the system.
- **Offline Query Processing**: Add functionality to handle queries offline using pre-saved or cached data to reduce dependency on live internet access.
