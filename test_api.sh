#!/bin/bash
echo "🧪 Testing API endpoints..."

BASE_URL="http://localhost:8000"

echo "1. Testing health check..."
curl -X GET "$BASE_URL/health" | jq '.'

echo -e "\n2. Testing question generation..."
curl -X POST "$BASE_URL/generate-questions" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python Programming", "difficulty": "simple", "num_questions": 3}' | jq '.'

echo -e "\n3. Testing text-to-speech..."
curl -X POST "$BASE_URL/text-to-speech" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test message"}' \
  --output test_speech.mp3

echo -e "\nAPI tests completed!"
