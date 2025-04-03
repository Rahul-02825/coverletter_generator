import os
import requests
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("API Key is missing. Check your .env file or environment variables.")
        
        print(f"[DEBUG] Using API Key: {api_key}... (truncated for security)")
        
        available_models = self.get_available_models(api_key)
        print("[DEBUG] Available models:", available_models)
        
        if "llama-3-70b-instruct" not in available_models:
            print("[WARNING] 'llama-3-70b-instruct' is not available. Switching to llama-3.3-70b-versatile.")
            model_name = "llama-3.3-70b-versatile"
        else:
            model_name = "mixtral-8x7b-instruct"
        
        self.llm = ChatGroq(
            temperature=0, 
            groq_api_key=api_key, 
            model_name=model_name
        )
        print(f"[DEBUG] Using model: {model_name}")

    def get_available_models(self, api_key):
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            response = requests.get("https://api.groq.com/v1/models", headers=headers)
            response.raise_for_status()
            return [model["id"] for model in response.json().get("data", [])]
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch available models: {e}")
            return []

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
            print(res)

        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are an individual student writing a cold email for a job opportunity. Write a cold email to a potential employer, explaining how your skills and experience align with the job requirements and how you can contribute effectively.

Include the most relevant links from the following list to showcase your work: {link_list}.

Requirements:

No preamble—start directly with the email.

Keep the tone professional yet natural, as a student would write.

Make it concise, engaging, and tailored to the job.

Avoid overly formal or robotic language—keep it genuine and confident.
            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        return res.content

if __name__ == "__main__":
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[ERROR] API Key is missing. Check your .env file.")
    else:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get("https://api.groq.com/v1/models", headers=headers)
        if response.status_code == 200:
            print("[DEBUG] Available models:", response.json())
        else:
            print(f"[ERROR] Failed to fetch models: {response.text}")