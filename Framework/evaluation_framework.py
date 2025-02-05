from openai import OpenAI
import requests
import os
from dotenv import load_dotenv
load_dotenv()


client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_evaluation_guideline():
    """
    Generates an evaluation guideline framework using OpenAI O1 Pro and DeepSeek R1.
    """
    # Define the evaluation criteria
    evaluation_areas = [
        "Collaboration & Communication",
        "Goal Achievement & Productivity",
        "Adaptability & Problem-Solving",
        "Leadership & Initiative",
        "Technical/Domain-Specific Proficiency",
        "Emotional Intelligence & Team Dynamics"
    ]
    
    # Construct the prompt
    prompt = f"""
    You are an expert in employee evaluation. Generate a structured evaluation guideline for the following areas:
    {', '.join(evaluation_areas)}.
    Provide measurable criteria and best practices for assessing each category.
    Return the response in JSON format only.
    """
    
    # Query OpenAI O1 Pro
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a professional HR evaluation expert."},
        {
            "role": "user",
            "content": prompt
        }
        ]
    )

    openai_guidelines = completion.choices[0].message
    
    # Query DeepSeek R1 Knowledge Base
    # deepseek_response = requests.post(
    #     "https://api.deepseek.com/v1/chat/completions",
    #     json={
    #         "model": "deepseek-r1",
    #         "messages": [{"role": "system", "content": "You are an expert HR analyst."},
    #                      {"role": "user", "content": prompt}]
    #     }
    # )
    # deepseek_guidelines = deepseek_response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    
    # # Merge both responses
    # final_guideline = {
    #     "OpenAI_O1_Pro": openai_guidelines,
    #     "DeepSeek_R1": deepseek_guidelines
    # }
    
    return openai_guidelines




# Example usage
# if __name__ == "__main__":
#     guideline = generate_evaluation_guideline()
#     print(guideline)
