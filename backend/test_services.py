import sys
from app.services.pdf_service import pdf_service
from app.services.search_service import search_service
from app.services.ai_service import ai_service

def test_pdf_chunking():
    print("Testing PDF chunking...")
    sample_text = "This is a sentence. " * 200
    chunks = pdf_service.chunk_text(sample_text, chunk_size=200, overlap=50)
    print(f"-> Generated {len(chunks)} chunks from text length {len(sample_text)}")
    assert len(chunks) > 0, "Should generate chunks"
    print("PDF chunking test PASSED!\n")

def test_web_search():
    print("Testing Web Search...")
    # Query something general
    results = search_service.search("India space program ISRO news", max_results=2)
    print(f"-> Found {len(results)} search results.")
    for idx, r in enumerate(results, 1):
        print(f"  [{idx}] {r['title']} - {r['link'][:50]}...")
    print("Web Search test PASSED!\n")

def test_ai_response():
    print("Testing AI Service...")
    messages = [{"role": "user", "content": "Tell me about BharatAI"}]
    response = ai_service.generate_chat_response(messages)
    print("-> AI Response:")
    print(response)
    print("AI Service test PASSED!\n")

if __name__ == "__main__":
    print("Starting BharatAI Backend Services Verification...\n")
    try:
        test_pdf_chunking()
        test_web_search()
        test_ai_response()
        print("ALL SERVICE TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    except Exception as e:
        print(f"TEST RUN FAILED: {e}")
        sys.exit(1)
