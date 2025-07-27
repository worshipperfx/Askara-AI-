import requests


BASE_URL = "http://localhost:8000"

def test_api():
    print("Testing FastAPI Exam Generator")
    print("=" * 50)
    
    # Test 1: health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test 2: generate question
    print("\n2. Testing question generation...")
    try:
        response = requests.post(f"{BASE_URL}/predict", 
                               json={"paper_code": "MATH101"})
        if response.status_code == 200:
            question_data = response.json()
            print(f"Question generated: {question_data['question'][:100]}...")
            print(f"Topic ID: {question_data['topic_id']}")
        else:
            print(f"Question generation failed: {response.text}")
            return
    except Exception as e:
        print(f"Question generation failed: {e}")
        return
    
    # Test 3: get answer
    print("\n3. Testing answer generation...")
    try:
        response = requests.post(f"{BASE_URL}/answer")
        if response.status_code == 200:
            answer_data = response.json()
            print(f"Answer generated: {answer_data['answer'][:100]}...")
        else:
            print(f"Answer generation failed: {response.text}")
            return
    except Exception as e:
        print(f"Answer generation failed: {e}")
        return
    
    # Test 4: ask for clarification
    print("\n4. Testing clarification...")
    try:
        response = requests.post(f"{BASE_URL}/clarify", 
                               json={"follow_up": "Can you explain this in simpler terms?"})
        if response.status_code == 200:
            clarify_data = response.json()
            print(f"Clarification: {clarify_data['clarification'][:100]}...")
        else:
            print(f"Clarification failed: {response.text}")
    except Exception as e:
        print(f"Clarification failed: {e}")
    
    # Test 5: get session status
    print("\n5. Testing session status...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"Session status: {status_data}")
        else:
            print(f"Session status failed: {response.text}")
    except Exception as e:
        print(f"Session status failed: {e}")
    
    # Test 6: get chat history
    print("\n6. Testing chat history...")
    try:
        response = requests.get(f"{BASE_URL}/history")
        if response.status_code == 200:
            history_data = response.json()
            print(f"Chat history length: {len(history_data['chat_history'])}")
            for entry in history_data['chat_history'][-2:]:  # show last 2 entries in the chat history
                print(f"   {entry[0]}: {entry[1][:50]}...")
        else:
            print(f"Chat history failed: {response.text}")
    except Exception as e:
        print(f"Chat history failed: {e}")
    
    print("\n" + "=" * 50)
    print("Testing complete!")

if __name__ == "__main__":
    test_api()