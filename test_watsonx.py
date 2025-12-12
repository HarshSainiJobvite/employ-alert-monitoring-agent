"""
Test script to verify WatsonX integration with LangChain.
This tests the WatsonX ChatModel before running the full agent.
"""
from config import Config

print("="*60)
print("🧪 Testing WatsonX Integration")
print("="*60)
print()

# Validate WatsonX configuration
print("📋 Checking WatsonX Configuration:")
print(f"  WATSONX_APIKEY: {'✅ Set' if Config.WATSONX_APIKEY else '❌ Missing'}")
print(f"  WATSONX_PROJECT_ID: {'✅ Set' if Config.WATSONX_PROJECT_ID else '❌ Missing'}")
print(f"  WATSONX_URL: {Config.WATSONX_URL}")
print(f"  USE_WATSONX: {Config.USE_WATSONX}")
print()

if not Config.WATSONX_APIKEY or not Config.WATSONX_PROJECT_ID:
    print("❌ WatsonX configuration incomplete!")
    print("   Please check your .env file")
    exit(1)

print("✅ WatsonX configuration is complete")
print()

# Test WatsonX LLM
print("🤖 Initializing WatsonX LLM...")
try:
    from langchain_ibm import WatsonxLLM

    llm = WatsonxLLM(
        model_id="ibm/granite-13b-chat-v2",
        url=Config.WATSONX_URL,
        apikey=Config.WATSONX_APIKEY,
        project_id=Config.WATSONX_PROJECT_ID,
        params={
            "decoding_method": "greedy",
            "max_new_tokens": 500,
            "temperature": 0.7,
            "top_k": 50,
            "top_p": 1
        }
    )

    print("✅ WatsonX LLM initialized successfully")
    print()

    # Test inference
    print("🔬 Testing WatsonX inference...")
    print()

    test_prompt = """Analyze this alert scenario:
    
Application: jhire
Error Type: NullPointerException
Total Errors: 147
Affected Users: 23
Affected Companies: 8

Provide 3 actionable recommendations for the SRE team.

Format your response as:
1. [First recommendation]
2. [Second recommendation]
3. [Third recommendation]
"""

    print("📤 Sending test prompt to WatsonX...")
    response = llm.invoke(test_prompt)

    print("📥 Response received:")
    print("-" * 60)
    print(response)
    print("-" * 60)
    print()

    print("✅ WatsonX integration test successful!")
    print()
    print("🎉 Your agent is ready to use WatsonX for AI reasoning!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print()
    print("   Please install required packages:")
    print("   pip install langchain-ibm ibm-watsonx-ai")
    exit(1)

except Exception as e:
    print(f"❌ Error testing WatsonX: {str(e)}")
    print()
    import traceback
    traceback.print_exc()
    exit(1)

print()
print("="*60)
print("Next steps:")
print("  1. Run the polling server: ./start_polling.sh")
print("  2. The agent will use WatsonX for all AI reasoning")
print("="*60)

