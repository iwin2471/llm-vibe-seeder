import os
from transformers import pipeline, set_seed
import torch
import requests
import sseclient
import json
import http

import lmstudio as lms
import yaml


class LLMManager:
    # model: Pipeline
    prompts: dict
    
    def __init__(self):
        # self.model = lms.llm("mn-darkest-universe-29b")
        self.prompts = self.load_prompts(os.path.join(os.path.dirname(__file__), "prompts.yaml"))
        # self.model = pipeline("Lucy-in-the-Sky/Mixtral-8x7B-Instruct-v0.1-Q4_K_M-GGUF", device=0 if torch.cuda.is_available() else -1)
            
    def load_prompts(self, prompts_file_path: str) -> dict:
        """
        Load prompts from a YAML file.
        """
        if not os.path.exists(prompts_file_path):
            raise FileNotFoundError(f"Prompts file not found: {prompts_file_path}")
        with open(prompts_file_path, 'r') as file:
            prompts = yaml.safe_load(file)
        return prompts
    
    def generate_prompt(self, prompt_type: str, **kwargs) -> str:
        prompt_template = self.prompts.get(prompt_type)
        if not prompt_template:
            raise ValueError(f"Prompt type '{prompt_type}' not found.")
        return prompt_template.format(**kwargs)
    
    def call_webui_api(self, prompt: str, max_tokens: int = 300, temperature = 0.9, top_p = 0.95, seed=-1) -> str:
        """
        Call text-generation-webui OpenAI-compatible API (v1/completions) using raw HTTP to avoid cutoff issues.
        """
            
        payload = {
                "model": "gpt-4",  # dummy name for OpenAI-compatible API
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "preset": "None"  # CRITICAL to bypass internal limits
            }

        try:
                conn = http.client.HTTPConnection("localhost", 5000, timeout=180)
                headers = {
                    "Content-Type": "application/json",
                    "Connection": "keep-alive"
                }

                conn.request("POST", "/v1/completions", body=json.dumps(payload), headers=headers)
                response = conn.getresponse()

                if response.status != 200:
                    print(f"❌ LLM returned error: {response.status} {response.reason}")
                    return "[ERROR]"

                raw_data = response.read().decode()
                conn.close()

                data = json.loads(raw_data)
                return data["choices"][0]["text"].strip()

        except Exception as e:
                print("❌ API call failed:", e)
                return "[ERROR]"


manager = LLMManager()
