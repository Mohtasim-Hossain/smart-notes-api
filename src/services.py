from openai import OpenAI
from .config import get_settings

\
settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)

async def get_summary(content: str) -> str:
    """Generates a summary of the provided content using OpenAI's free-tier API model."""
    try:
        # print(f"Summarizing content with length: {len(content)}")

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": f"Summarize the following text:\n{content}"}
            ],
            max_tokens=50,
            temperature=0.5
        )

        summary = completion.choices[0].message['content'].strip()
        # print(f"Generated summary: {summary}")  
        return summary
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Could not generate summary"
