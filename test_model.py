from models.manager import manager

response = manager.generate(
    "Say hello from BharatAI."
)

print(response)