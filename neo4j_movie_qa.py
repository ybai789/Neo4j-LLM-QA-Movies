from neo4j import GraphDatabase
import re
import string
from typing import Dict, List, Tuple, Optional
import logging

class MovieKnowledgeGraphQA:
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize the QA system with Neo4j connection.

        Args:
            uri: Neo4j database URI
            user: Username
            password: Password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Define question patterns and corresponding query templates
        self.question_patterns = self.define_question_patterns()

    def define_question_patterns(self) -> Dict:
        """Define question patterns and their corresponding query templates."""
        return {
            "director_movies": {
                "patterns": [
                    r"what movies did (.*) direct",
                    r"show me movies directed by (.*)",
                    r"list (.*)'s movies as director"
                ],
                "query": """
                    MATCH (p:Person)-[:DIRECTED]->(m:Movie)
                    WHERE p.name = $param1
                    RETURN m.name as movie, m.year as year, m.rating as rating
                    ORDER BY m.rating DESC
                """
            },
            "actor_movies": {
                "patterns": [
                    r"what movies did (.*) act in",
                    r"show me movies starring (.*)",
                    r"which movies featured (.*)"
                ],
                "query": """
                    MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
                    WHERE p.name = $param1
                    RETURN m.name as movie, m.year as year, m.rating as rating
                    ORDER BY m.rating DESC
                """
            },
            "movie_info": {
                "patterns": [
                    r"tell me about the movie (.*)",
                    r"what is the information for (.*)",
                    r"show details of movie (.*)"
                ],
                "query": """
                    MATCH (m:Movie)
                    WHERE m.name = $param1
                    OPTIONAL MATCH (p1:Person)-[:DIRECTED]->(m)
                    OPTIONAL MATCH (p2:Person)-[:ACTED_IN]->(m)
                    OPTIONAL MATCH (m)-[:BELONGS_TO]->(g:Genre)
                    RETURN m.name as movie, m.year as year, m.rating as rating,
                           m.certificate as certificate, m.run_time as runtime,
                           collect(DISTINCT p1.name) as directors,
                           collect(DISTINCT p2.name) as actors,
                           collect(DISTINCT g.name) as genres
                """
            }
        }

    def close(self):
        """Close the database connection."""
        self.driver.close()

    def match_question(self, question: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Match the input question against defined patterns.

        Args:
            question: Input question string.

        Returns:
            Tuple containing query type and extracted parameter (if any).
        """
        question = question.strip()
        for query_type, data in self.question_patterns.items():
            for pattern in data["patterns"]:
                match = re.match(pattern, question, re.IGNORECASE)
                if match:
                    param = match.group(1).strip(string.punctuation) if len(match.groups()) > 0 else None
                    return query_type, param
        return None, None

    def execute_query(self, query: str, param: Optional[str] = None) -> List[Dict]:
        """
        Execute the Cypher query against the Neo4j database.

        Args:
            query: Cypher query string.
            param: Parameter for the query.

        Returns:
            List of query results.
        """
        try:
            with self.driver.session() as session:
                if param:
                    # Ensure param is passed as a string
                    results = list(session.run(query, param1=str(param)))
                else:
                    results = list(session.run(query))
                return [record.data() for record in results]
        except Exception as e:
            self.logger.error(f"Error executing query: {query} with param: {param}\n{e}")
            return []

    def answer_question(self, question: str) -> str:
        """
        Process a natural language question and return an answer.

        Args:
            question: Input question string.

        Returns:
            Formatted answer string.
        """
        try:
            # Match question pattern
            query_type, param = self.match_question(question)
            if not query_type:
                return "I'm sorry, I don't understand that question."

            # Get the query template
            query = self.question_patterns[query_type]["query"]

            # Execute the query
            results = self.execute_query(query, param)

            # Format the response
            return self.format_response(query_type, results)
        except Exception as e:
            self.logger.error(f"Error processing question '{question}': {str(e)}")
            return "I encountered an error while processing your question."

    def format_response(self, query_type: str, results: List[Dict]) -> str:
        """
        Format the query results into a readable response.

        Args:
            query_type: Type of query executed.
            results: Query results from Neo4j.

        Returns:
            Formatted response string.
        """
        if not results:
            return "No results found."

        response = []
        for result in results:
            if query_type in ["director_movies", "actor_movies"]:
                response.append(f"{result['movie']} ({result['year']}) - Rating: {result['rating']}")
            elif query_type == "movie_info":
                response.append(f"Movie: {result['movie']} ({result['year']})\n"
                                f"Rating: {result['rating']}\n"
                                f"Certificate: {result['certificate']}\n"
                                f"Runtime: {result['runtime']}\n"
                                f"Directors: {', '.join(result['directors'])}\n"
                                f"Genres: {', '.join(result['genres'])}\n"
                                f"Actors: {', '.join(result['actors'])}")
            else:
                response.append(f"{result}")
        return "\n".join(response)


def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Neo4j connection configuration
    uri = "neo4j://localhost:7687"
    user = "neo4j"
    password = "neo4j123"

    # Create QA system instance
    qa_system = MovieKnowledgeGraphQA(uri, user, password)

    print("Welcome to the Movie Knowledge Graph QA System!")
    print("Type 'exit' to quit.\n")

    try:
        while True:
            question = input("Ask a question: ").strip()
            if question.lower() == "exit":
                break
            print("\nAnswer:")
            print(qa_system.answer_question(question))
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        qa_system.close()


if __name__ == "__main__":
    main()

