## Neo4j and LLM-Enhanced Movie Knowledge Graph QA System

## Introduction

This repository provides a question-answering system that integrates a **Neo4j knowledge graph** with a chatbot interface, enhanced by **Large Language Model (LLM)** capabilities. The system dynamically processes user queries, extracts intent and entities using an LLM, generates context-aware Cypher queries for the Neo4j database, and formats results into natural language responses. It offers a flexible and interactive platform for exploring complex movie-related queries.

## Features

### **1. LLM-Driven Natural Language Understanding**
- Automatically extracts **intents** (e.g., `movie_search`, `person_info`) and **entities** (e.g., director names, movie titles, genres) from complex user queries using GPT-based LLM.
- Eliminates the need to predefine rigid question patterns or rules, enabling more **natural interactions**.

### **2. Dynamic Cypher Query Generation**
- Uses LLM to dynamically create **Cypher queries** based on user questions and the schema of the Neo4j movie knowledge graph.
- Supports advanced, multi-step reasoning and context-aware query generation.

### **3. Neo4j Knowledge Graph Integration**
- Leverages a structured movie knowledge graph stored in Neo4j, which includes:
  - Nodes: Movies, People, Genres
  - Relationships: Directed, Acted In, Wrote, Belongs To
- Provides efficient querying and retrieval of detailed movie information.

### **4. Gradio Chatbot Interface**
- A user-friendly chatbot built using **Gradio** enables interactive querying.
- Users can input natural language questions and receive detailed, conversational answers.
- Responses are enriched with statistics and interesting insights extracted from the database.

## How It Works

<img src=".\images\graph.png" alt="arch" style="zoom:40%;" />

## How It Works

This project integrates a **Neo4j knowledge graph** and **Large Language Models (LLMs)** to create an interactive question-answering system for exploring movie-related data. By leveraging the **IMDB Top 250 Movies dataset**, **Neo4j** for knowledge representation, and **OpenAI's LLM API**, the system dynamically interprets user queries, retrieves relevant data, and generates detailed responses in natural language.

------

### 1. **Build the Knowledge Graph**

- The knowledge graph is built using the **IMDB Top 250 Movies dataset**, representing movies, people (directors, actors, writers), and genres.
- The graph is modeled in Neo4j, with:
  - **Nodes**: `Movie`, `Person`, `Genre`
  - **Relationships**: `DIRECTED`, `ACTED_IN`, `WROTE`, `BELONGS_TO`
- Relationships allow for efficient exploration of interconnected movie data.

------

### 2. **Query Understanding with LLM**

- Dynamic Query Interpretation:
  - User queries are processed using OpenAI's **LLM** to extract **intent** (e.g., `movie_search`, `person_info`) and **entities** (e.g., movie titles, director names).
- Flexible Natural Language Processing:
  - Unlike traditional methods requiring predefined patterns, the LLM dynamically generates structured Cypher queries tailored to user input.

------

### 3. **Execute Cypher Query in Neo4j**

- The system executes LLM-generated Cypher queries on the **Neo4j knowledge graph** to retrieve relevant information.

- Example query:

  ```cypher
  MATCH (p:Person)-[:DIRECTED]->(m:Movie)
  WHERE p.name = 'Christopher Nolan'
  RETURN m.name AS movie, m.year AS year, m.rating AS rating
  ORDER BY m.rating DESC
  ```

------

### 4. **Generate Context-Aware Responses**

- Query results from Neo4j are passed back to the LLM, which formats them into **engaging and detailed natural language responses**.
- Responses include:
  - Movie titles, ratings, and release years
  - Relationships (e.g., directors and actors)
  - Highlights and patterns (e.g., top-rated movies, genres)

------

### 5. **Interactive Gradio Chatbot**

- The Gradio interface

   enables user-friendly interaction with the system:

  - Users type queries such as:
    - "What movies did Christopher Nolan direct?"
    - "Show me movies starring Leonardo DiCaprio."
  - The chatbot responds with detailed, conversational answers.

- The chatbot runs as a **web-based application**, providing real-time query and response functionality.

------

### Benefits of Combining Neo4j and LLM

- Structured Knowledge Graph:
  - Neo4j efficiently stores and retrieves highly relational data (e.g., movie-person relationships).
- Natural Language Understanding:
  - LLMs enable dynamic interpretation of free-form user queries without predefined rules.
- Enhanced Responses:
  - The system provides not just raw data but insightful and engaging answers, enriched by the LLM.

------

This project demonstrates how Neo4j's graph capabilities and LLM's natural language processing power can be combined to create a robust and interactive question-answering system for movie exploration.

## Example output

<img src=".\images\llm_response_example.png" alt="arch" />

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ybai789/Neo4j-LLM-QA-Movies.git
   cd Neo4j-LLM-QA-Movies
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables by creating a `.env` file in the root directory:

   ```bash
   OPENAI_API_KEY=your_openai_api_key
   ```

4. Install Neo4j and modify user and password in the Python source files

## Usage

### 1. **Build the Knowledge Base**

To create a knowledge base from the IMDB Top 250 Movies dataset and store it in Neo4j, run the following command:

```bash
python build_neo4j_imdb_graph.py
```

This script processes the dataset and populates the Neo4j database with nodes and relationships representing movies, directors, actors, genres, and more.

------

### 2. **Query the Knowledge Base without LLM Enhancements**

You can query the knowledge base directly using Neo4j without leveraging LLM capabilities:

```bash
python neo4j_movie_qa.py
```

This script enables simple question-answering functionality based on predefined patterns and Cypher queries.

------

### 3. **Query the Knowledge Base with LLM Enhancements**

To enhance the querying process with natural language understanding and reasoning powered by an LLM, use:

```bash
python llm_movie_qa.py
```

This script integrates OpenAI's GPT models to understand and process complex natural language queries, enhancing the system's ability to interpret intent and extract relevant information.

------

### 4. **Launch the Gradio Chatbot Interface**

For an interactive web-based experience, launch the Gradio-powered chatbot interface:

```bash
python gradio_movie_qa.py
```

This will start a web application where you can:

- Enter natural language queries.
- Get detailed responses powered by Neo4j and LLM.
- Interact with the knowledge base in a conversational manner.

Simply open the provided URL in your browser to start interacting with the system.