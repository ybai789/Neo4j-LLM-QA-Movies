import pandas as pd
from neo4j import GraphDatabase
from typing import Dict, List
import logging


class IMDBKnowledgeGraph:
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize Neo4j connection

        Args:
            uri: Neo4j database URI
            user: Username
            password: Password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.logger = logging.getLogger(__name__)

    def close(self):
        """Close the database connection"""
        self.driver.close()

    def create_constraints_and_indexes(self):
        """Create constraints and indexes for better performance"""
        with self.driver.session() as session:
            # Create constraints
            constraints = [
                "CREATE CONSTRAINT movie_id IF NOT EXISTS FOR (m:Movie) REQUIRE m.id IS UNIQUE",
                "CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT genre_id IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE"
            ]

            # Create indexes
            indexes = [
                "CREATE INDEX movie_name IF NOT EXISTS FOR (m:Movie) ON (m.name)",
                "CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name)"
            ]

            for constraint in constraints:
                session.run(constraint)
            for index in indexes:
                session.run(index)

    def create_movie_node(self, tx, movie_data: Dict):
        """Create a movie node with its properties"""
        query = """
        MERGE (m:Movie {id: $rank})
        SET m.name = $name,
            m.year = $year,
            m.rating = $rating,
            m.certificate = $certificate,
            m.run_time = $run_time,
            m.tagline = $tagline,
            m.budget = $budget,
            m.box_office = $box_office
        """
        tx.run(query, **movie_data)

    def create_genre_relationships(self, tx, movie_id: int, genres: List[str]):
        """Create relationships between movies and genres"""
        query = """
        MATCH (m:Movie {id: $movie_id})
        MERGE (g:Genre {name: $genre})
        MERGE (m)-[:BELONGS_TO]->(g)
        """
        for genre in genres:
            tx.run(query, movie_id=movie_id, genre=genre.strip())

    def create_person_relationships(self, tx, movie_id: int, role_type: str, persons: List[str]):
        """Create relationships between people and movies"""
        query = f"""
        MATCH (m:Movie {{id: $movie_id}})
        MERGE (p:Person {{name: $person}})
        MERGE (p)-[:{role_type}]->(m)
        """
        for person in persons:
            tx.run(query, movie_id=movie_id, person=person.strip())

    def import_data(self, csv_path: str):
        """Import data from CSV file into Neo4j"""
        df = pd.read_csv(csv_path)

        with self.driver.session() as session:
            for _, row in df.iterrows():
                try:
                    # Create movie node
                    movie_data = {
                        'rank': int(row['rank']),
                        'name': row['name'],
                        'year': int(row['year']),
                        'rating': float(row['rating']),
                        'certificate': row['certificate'],
                        'run_time': row['run_time'],
                        'tagline': row['tagline'],
                        'budget': row['budget'],
                        'box_office': row['box_office']
                    }
                    session.execute_write(self.create_movie_node, movie_data)

                    # Create genre relationships
                    genres = row['genre'].split(',')
                    session.execute_write(self.create_genre_relationships, movie_data['rank'], genres)

                    # Create director relationships
                    directors = row['directors'].split(',')
                    session.execute_write(self.create_person_relationships, movie_data['rank'], 'DIRECTED', directors)

                    # Create writer relationships
                    writers = row['writers'].split(',')
                    session.execute_write(self.create_person_relationships, movie_data['rank'], 'WROTE', writers)

                    # Create actor relationships
                    actors = row['casts'].split(',')
                    session.execute_write(self.create_person_relationships, movie_data['rank'], 'ACTED_IN', actors)

                    self.logger.info(f"Successfully processed movie: {movie_data['name']}")
                except Exception as e:
                    self.logger.error(f"Error processing movie {row['name']}: {str(e)}")


def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Neo4j connection configuration
    uri = "neo4j://localhost:7687"
    user = "neo4j"
    password = "neo4j123"

    # CSV file path
    csv_path = "IMDB_Top_250_Movies.csv"

    try:
        # Create knowledge graph instance
        kg = IMDBKnowledgeGraph(uri, user, password)

        # Create constraints and indexes
        kg.create_constraints_and_indexes()

        # Import data
        kg.import_data(csv_path)

        logging.info("Data import completed successfully!")

    except Exception as e:
        logging.error(f"Error: {str(e)}")

    finally:
        # Close connection
        kg.close()


if __name__ == "__main__":
    main()
