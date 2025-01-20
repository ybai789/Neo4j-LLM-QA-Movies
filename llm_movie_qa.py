from neo4j import GraphDatabase
from typing import Dict, List, Optional
import logging
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is missing. Please set it in the .env file.")


class EnhancedMovieKnowledgeGraphQA:
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str, openai_api_key: str):
        """
        Initialize the enhanced QA system with Neo4j and OpenAI connections.

        Args:
            neo4j_uri: Neo4j database URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            openai_api_key: OpenAI API key
        """
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.llm_client = OpenAI(api_key=openai_api_key)
        self.logger = logging.getLogger(__name__)

    def close(self):
        """Close the database connection."""
        self.driver.close()

    def get_question_intent(self, question: str) -> Dict:
        """
        Analyze the intent of the user's question and extract entities.

        Args:
            question: User's natural language question.

        Returns:
            A dictionary containing:
                - primary_intent: The primary intent of the question (e.g., "movie_search", "person_info").
                - entities: Extracted entities (e.g., movie names, actor names, genres).
        """
        try:
            # Define the prompt for the LLM
            system_prompt = """
            Analyze the following question and extract its intent and entities.
            The output should be a JSON object with the following fields:
            - primary_intent: A string describing the main intent (e.g., "movie_search", "person_info").
            - entities: A dictionary with keys such as "movies", "people", or "genres", 
              each containing a list of relevant names or terms extracted from the question.
            """
            user_prompt = f"Question: {question}"

            # Call OpenAI's API
            response = self.llm_client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0
            )

            # Parse and return the response as a dictionary
            return json.loads(response.choices[0].message.content.strip())

        except Exception as e:
            self.logger.error(f"Error analyzing question intent: {e}")
            return {"primary_intent": None, "entities": {}}

    def generate_cypher_query(self, question: str) -> str:
        """
        Use LLM to generate a Cypher query from a natural language question.

        Args:
            question: Natural language question

        Returns:
            Generated Cypher query
        """
        system_prompt = """
        You are a Cypher query generator for a movie knowledge graph with the following schema:
        Nodes:
        - Movie (properties: id, name, year, rating, certificate, run_time, tagline, budget, box_office)
        - Person (properties: name)
        - Genre (properties: name)
        
        Relationships:
        - (Person)-[:DIRECTED]->(Movie)
        - (Person)-[:ACTED_IN]->(Movie)
        - (Person)-[:WROTE]->(Movie)
        - (Movie)-[:BELONGS_TO]->(Genre)
        
        Generate only the Cypher query without any explanation or additional text. 
        """
        user_prompt = f"Generate a Cypher query for the question: {question}"

        response = self.llm_client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )

        # Sanitize the response to remove formatting issues
        query = response.choices[0].message.content.strip()
        if query.startswith("```"):
            query = query.strip("```").strip()  # Remove triple backticks if present
        return query

    def execute_query(self, cypher_query: str) -> List[Dict]:
        """
        Execute the generated Cypher query on Neo4j.

        Args:
            cypher_query: Cypher query string

        Returns:
            List of query results
        """
        try:
            with self.driver.session() as session:
                results = list(session.run(cypher_query))
                return [record.data() for record in results]
        except Exception as e:
            self.logger.error(f"Error executing query: {cypher_query}\n{e}")
            return []

    def generate_context_aware_answer(self, question: str, query_results: List[Dict]) -> str:
        """
        Use LLM to generate a natural language answer with query results.

        Args:
            question: Original question
            query_results: Results from Neo4j query

        Returns:
            Natural language answer
        """
        system_prompt = """
        You are a helpful movie information assistant. Generate a natural, conversational response 
        using the provided query results. Keep the following guidelines in mind:
        - Be concise but informative
        - Include relevant numbers and statistics when available
        - Use a friendly, conversational tone
        - Highlight interesting connections or patterns in the data
        - If no results are found, suggest possible reasons or alternative queries
        """
        user_prompt = f"""
        Question: {question}
        
        Query Results: {json.dumps(query_results, indent=2)}
        
        Generate a natural language response based on these results.
        """

        response = self.llm_client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    def handle_complex_query(self, question: str) -> str:
        """
        Handle complex queries requiring multiple steps or reasoning.

        Args:
            question: Complex natural language question

        Returns:
            Comprehensive answer
        """
        try:
            # Generate Cypher query using LLM
            cypher_query = self.generate_cypher_query(question)
            self.logger.info(f"Generated Cypher Query: {cypher_query}")

            # Execute Cypher query on Neo4j
            query_results = self.execute_query(cypher_query)

            # Generate context-aware natural language answer
            answer = self.generate_context_aware_answer(question, query_results)

            return answer
        except Exception as e:
            self.logger.error(f"Error handling query '{question}': {e}")
            return "I encountered an error while processing your question. Please try again."


def main():
    # Configuration
    neo4j_uri = "neo4j://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "neo4j123"

    # Create QA system instance
    qa_system = EnhancedMovieKnowledgeGraphQA(neo4j_uri, neo4j_user, neo4j_password, OPENAI_API_KEY)

    print("Enhanced Movie Knowledge Graph QA System")
    print("Type 'exit' to quit")

    try:
        while True:
            question = input("\nAsk a question: ").strip()
            if question.lower() == "exit":
                break

            # Process the question and generate an answer
            answer = qa_system.handle_complex_query(question)
            print("\nAnswer:")
            print(answer)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        qa_system.close()


if __name__ == "__main__":
    main()

