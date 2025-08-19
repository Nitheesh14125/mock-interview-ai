import requests
import json
import time

BASE_URL = "http://localhost:8000"

def example_interview_flow():
    """Example of how to use the interview API step by step"""
    
    print("🚀 Starting Example Interview Flow")
    print("=" * 50)
    
    # Step 1: Start interview session
    print("1. Starting interview session...")
    start_request = {
        "topic": "Python Programming",
        "difficulty": "simple",
        "num_questions": 3
    }
    
    response = requests.post(f"{BASE_URL}/start-interview", json=start_request)
    if response.status_code != 200:
        print(f"❌ Error starting interview: {response.text}")
        return
    
    session_data = response.json()
    session_id = session_data["session_id"]
    
    print(f"✅ Session started: {session_id}")
    print(f"📝 Greeting: {session_data['greeting']}")
    print(f"❓ First Question: {session_data['current_question']}")
    print(f"📊 Progress: {session_data['question_number']}/{session_data['total_questions']}")
    
    # Step 2: Submit answers for each question
    sample_answers = [
        "Python is a high-level programming language that is easy to learn and widely used.",
        "A list is mutable and ordered, while a tuple is immutable and ordered.",
        "A function is a block of reusable code that performs a specific task."
    ]
    
    for i, answer in enumerate(sample_answers):
        print(f"\n--- Question {i + 1} ---")
        print(f"💭 Submitting answer: {answer}")
        
        # Submit answer
        answer_request = {
            "session_id": session_id,
            "answer": answer
        }
        
        response = requests.post(f"{BASE_URL}/submit-answer", json=answer_request)
        if response.status_code != 200:
            print(f"❌ Error submitting answer: {response.text}")
            return
        
        result = response.json()
        print(f"✅ {result['message']}")
        
        if result["status"] == "completed":
            print("\n🎉 Interview completed!")
            print(f"📊 Feedback: {result['feedback']}")
            break
        else:
            print(f"❓ Next Question: {result['next_question']}")
            print(f"📊 Progress: {result['question_number']}/{result['total_questions']}")
        
        time.sleep(1)  # Small delay for demo
    
    # Step 3: Check final session status
    print(f"\n3. Checking final session status...")
    response = requests.get(f"{BASE_URL}/session/{session_id}")
    if response.status_code == 200:
        final_status = response.json()
        print(f"✅ Final Status: {json.dumps(final_status, indent=2)}")

def test_individual_endpoints():
    """Test individual endpoints"""
    
    print("\n🧪 Testing Individual Endpoints")
    print("=" * 50)
    
    # Test health check
    print("1. Health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ Health: {response.json()}")
    
    # Test question generation
    print("\n2. Generating questions...")
    question_request = {
        "topic": "JavaScript",
        "difficulty": "medium", 
        "num_questions": 2
    }
    response = requests.post(f"{BASE_URL}/generate-questions", json=question_request)
    print(f"✅ Questions: {json.dumps(response.json(), indent=2)}")
    
    # Test text-to-speech
    print("\n3. Testing text-to-speech...")
    tts_request = {"text": "This is a test message for text to speech"}
    response = requests.post(f"{BASE_URL}/text-to-speech", json=tts_request)
    if response.status_code == 200:
        with open("test_audio.mp3", "wb") as f:
            f.write(response.content)
        print("✅ Audio file saved as test_audio.mp3")
    
    # List sessions
    print("\n4. Listing sessions...")
    response = requests.get(f"{BASE_URL}/sessions")
    print(f"✅ Sessions: {response.json()}")

if __name__ == "__main__":
    print("🎯 Mock Interview API Client Example")
    print("Make sure the API server is running on http://localhost:8000")
    print()
    
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Server is not running. Please start it with ./run_api.sh")
            exit(1)
        
        print("✅ Server is running!")
        
        # Run examples
        example_interview_flow()
        test_individual_endpoints()
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Please start it with ./run_api.sh")
    except Exception as e:
        print(f"❌ Error: {e}")
