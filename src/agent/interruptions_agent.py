from src.app import openai_client


async def check_for_one_message(message):
    with open("./src/assets/prompts/ask_prompt.txt", "r") as f:
        prompt = f.read()
        response = await openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"60-100 messages context:\n\n"
                                    f"{None}"
                        }
                    ]
                }
            ],
            response_format={
                "type": "text"
            },
            temperature=0.8,
            max_completion_tokens=5000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            user=f"{message.from_user.id}",
            metadata={
                "type": "group_conversation",
                "chat": f"{message.chat.id}",
                "user": f"{message.from_user.id}"
            }
        )
        resp: str = response.choices[0].message.content

async def check_in_context():
    pass

async def check_for_interruptions_needed(message):
    pass