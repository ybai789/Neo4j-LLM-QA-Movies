import gradio as gr
from typing import List, Tuple
import logging
from llm_movie_qa import EnhancedMovieKnowledgeGraphQA
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is missing. Please set it in the .env file.")

class MovieKnowledgeGraphUI:
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str, openai_api_key: str):
        """
        Initialize the UI system with QA backend.

        Args:
            neo4j_uri: Neo4j database URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            openai_api_key: OpenAI API key
        """
        self.qa_system = EnhancedMovieKnowledgeGraphQA(
            neo4j_uri, neo4j_user, neo4j_password, openai_api_key
        )
        self.logger = logging.getLogger(__name__)

    def process_query(self, question: str, history: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """
        Process a user query and update chat history.

        Args:
            question: User's question.
            history: Chat history.

        Returns:
            Updated chat history.
        """
        try:
            # Generate answer
            answer = self.qa_system.handle_complex_query(question)

            # Update chat history
            history.append((question, answer))

            return history
        except Exception as e:
            self.logger.error(f"Error processing question: {str(e)}")
            error_msg = "I encountered an error while processing your question. Please try again."
            history.append((question, error_msg))
            return history

    def create_interface(self) -> gr.Blocks:
        """
        Create the Gradio interface.

        Returns:
            Gradio Blocks interface.
        """
        with gr.Blocks(title="Movie Knowledge Graph QA System") as interface:
            gr.Markdown("# Movie Knowledge Graph QA System\nAsk questions about movies, directors, actors, and more!")

            with gr.Row():
                chatbot = gr.Chatbot(label="Chat History", height=400)

            question_input = gr.Textbox(label="Your Question", placeholder="Type your question here...", lines=2)
            submit_btn = gr.Button("Ask")
            clear_btn = gr.Button("Clear")

            submit_btn.click(
                fn=self.process_query,
                inputs=[question_input, chatbot],
                outputs=[chatbot]
            )

            clear_btn.click(fn=lambda: [], inputs=[], outputs=[chatbot])

            return interface

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Configuration
    neo4j_uri = "neo4j://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "neo4j123"

    # Create UI instance
    ui = MovieKnowledgeGraphUI(neo4j_uri, neo4j_user, neo4j_password, OPENAI_API_KEY)

    # Launch Gradio interface
    interface = ui.create_interface()
    interface.launch(share=True)

if __name__ == "__main__":
    main()


