import pandas as pd
import random
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
import logging

load_dotenv(dotenv_path="C:/Users/Marvellous/Desktop/Exam Prediction Rephrasing/backend_/python.env")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    client = OpenAI(api_key=api_key)
    logger.info("OpenAI client initialized successfully using environment variable.")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    raise

# Load data with error handling
try:
    topics_df = pd.read_csv(r"C:\Users\Marvellous\Desktop\Exam Prediction Rephrasing\topic_only.csv")
    questions_df = pd.read_csv(r"C:\Users\Marvellous\Desktop\Exam Prediction Rephrasing\merged_with_topics.csv")
    topics_df['Count'] = pd.to_numeric(topics_df['Count'], errors='coerce')
    topics_df['Weight'] = topics_df['Count'] / topics_df['Count'].sum()
    logger.info("Data loaded successfully")
except FileNotFoundError as e:
    logger.error(f"Data file not found: {e}")
    raise
except Exception as e:
    logger.error(f"Error loading data: {e}")
    raise

# Index questions by topic
example_questions = {
    row['Topic']: questions_df[questions_df['topic'] == row['Topic']]['text'].tolist()
    for _, row in topics_df.iterrows()
}

# Global state for now
state = {
    "current_question": None,
    "current_answer": None,
    "clarification_log": [],
    "chat_history": [],
    "topic_id": None,
    "examples": []
}

def call_openai_with_retry(messages, model="gpt-4o", max_retries=3, delay=1):
    """
    Call OpenAI API with retry logic and error handling
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"API call attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
            else:
                logger.error(f"All {max_retries} API call attempts failed")
                raise

def generate_question():
    """
    Generate a new question based on topic weights and examples
    """
    try:
        # Sample topic based on weights
        topic_row = topics_df.sample(weights=topics_df["Weight"])
        topic_id = int(topic_row["Topic"].values[0])
        examples = example_questions.get(topic_id, [])

        if not examples:
            logger.warning(f"No examples available for topic {topic_id}")
            return {"error": "No examples available for this topic."}

        # Sample up to 3 examples
        sample = random.sample(examples, min(3, len(examples)))

        prompt = f"""
You are an exam question generator.
Topic ID: {topic_id}

Based on the following past exam questions:
{chr(10).join(f"- {q}" for q in sample)}

Generate a new, original question that fits the same topic and difficulty level.
The question should be clear, specific, and test similar concepts.
"""

        question = call_openai_with_retry([{"role": "user", "content": prompt}])

        # Update state
        state.update({
            "topic_id": topic_id,
            "examples": sample,
            "current_question": question,
            "clarification_log": [],
            "current_answer": None,
        })
        state["chat_history"].append(["system", f"📘 Question: {question}"])
        
        logger.info(f"Generated question for topic {topic_id}")
        return {
            "question": question,
            "topic_id": topic_id,
            "examples": sample
        }
    
    except Exception as e:
        logger.error(f"Error generating question: {e}")
        return {"error": f"Failed to generate question: {str(e)}"}

def show_answer():
    """
    Generate and display the answer to the current question
    """
    try:
        if not state.get("current_question"):
            return {"error": "No current question to answer."}

        prompt = f"""
You are an expert exam tutor.

Please provide a comprehensive answer to this exam question:
{state['current_question']}

Your answer should:
- Be clear and well-structured
- Include step-by-step reasoning where appropriate
- Provide concrete examples if helpful
- Be at an appropriate academic level
"""

        answer = call_openai_with_retry([{"role": "user", "content": prompt}])
        
        state["current_answer"] = answer
        state["chat_history"].append(["system", f"📝 Answer: {answer}"])
        
        logger.info("Generated answer successfully")
        return {"answer": answer}
    
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return {"error": f"Failed to generate answer: {str(e)}"}

def clarify(follow_up: str):
    """
    Handle follow-up questions and clarifications
    """
    try:
        if not follow_up or follow_up.strip().lower() in ["no", "none", "nothing"]:
            state["chat_history"].append(["user", "No further questions."])
            state["chat_history"].append(["system", "Ready for next question."])
            return {"message": "No clarification needed. Ready for next question!"}

        if not state.get("current_question"):
            return {"error": "No current question to clarify."}

        prompt = f"""
You are a helpful exam tutor.

Original Question: {state['current_question']}

A student has asked this follow-up question:
"{follow_up}"

Please provide a clear, helpful explanation that addresses their specific question.
Be patient and educational in your response.
"""

        clarification = call_openai_with_retry([{"role": "user", "content": prompt}])
        
        state["clarification_log"].append((follow_up, clarification))
        state["chat_history"].append(["user", follow_up])
        state["chat_history"].append(["system", f"💡 Clarification: {clarification}"])
        
        logger.info("Provided clarification successfully")
        return {"clarification": clarification}
    
    except Exception as e:
        logger.error(f"Error providing clarification: {e}")
        return {"error": f"Failed to provide clarification: {str(e)}"}

def get_chat_history():
    """
    Return the current chat history
    """
    return {"chat_history": state["chat_history"]}

def reset_session():
    """
    Reset the current session state
    """
    global state
    state = {
        "current_question": None,
        "current_answer": None,
        "clarification_log": [],
        "chat_history": [],
        "topic_id": None,
        "examples": []
    }
    logger.info("Session reset")
    return {"message": "Session reset successfully"}

# Example usage functions
def run_example_session():
    """
    Run an example session for testing
    """
    print("=== Example Session ===")
    
    # Generate a question
    result = generate_question()
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print(f"Question: {result['question']}")
    print(f"Topic ID: {result['topic_id']}")
    
    # Show answer
    answer_result = show_answer()
    if "error" in answer_result:
        print(f"Error: {answer_result['error']}")
        return
    
    print(f"Answer: {answer_result['answer']}")
    
    # Example clarification
    clarify_result = clarify("Can you explain this in simpler terms?")
    if "error" in clarify_result:
        print(f"Error: {clarify_result['error']}")
        return
    
    print(f"Clarification: {clarify_result['clarification']}")

if __name__ == "__main__":
    # Run example session when script is executed directly
    run_example_session()