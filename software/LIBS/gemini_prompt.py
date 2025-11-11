import os
import time
import requests
import csv
from datetime import datetime
from typing import Optional, Dict, List
from threading import Lock
from serverId import quilla_Server

# Configuration
LOG_URL = quilla_Server()
appdata = os.getenv('APPDATA')
quilla_folder = os.path.join(appdata, ".Quilla")

LOGIN_PATH = os.path.join(quilla_folder, "login_data.csv")
SIGN_PATH = os.path.join(quilla_folder, "signup_data.csv")
COST_LOG_PATH = os.path.join(quilla_folder, "gemini_costs.csv")

# 🔑 API Keys (Hardcoded for now)
API_KEYS = [
    "AIzaSyD_TAcUoafTPJoUr0jqN-SUZkvFRUC5Fk4",
    "AIzaSyBHO1KjVbK73gy9JQ0giXK37jZnjPGOCNg",
    "AIzaSyC92MUhA8-o3VhRC4vk5gw7auXpwYmRK_8",
    "AIzaSyCPJ3AN9n5ZUeWWrQCrG3ijyNzX6dSfF80",
    "AIzaSyDXA-qxBQE0fZkkTnCYXWZd4rtz_WiWsNI",
    "AIzaSyD_xZFIGTkrOwHCv_eAiKOSILUMpiLOy3w"
    
]

# Pricing per 1M tokens (in USD)
PRICING = {
    'gemini-1.5-flash': {'input': 0.075, 'output': 0.30},
    'gemini-1.5-pro': {'input': 1.25, 'output': 5.00},
    'gemini-1.0-pro': {'input': 0.50, 'output': 1.50},
    'gemini-2.0-flash-exp': {'input': 0.00, 'output': 0.00},
    'gemini-2.5-flash-lite': {'input': 0.00, 'output': 0.00},
    'gemini-2.5-flash': {'input': 0.30, 'output': 2.50}
}

USD_TO_INR = 88.73


class GeminiApiClient:
    """Thread-safe Gemini API client with cost tracking and user management."""
    
    def __init__(self, default_model: str = 'gemini-2.5-flash'):
        self.default_model = default_model
        self.username: Optional[str] = None
        self.email: Optional[str] = None
        self._last_key_index = -1
        self._key_lock = Lock()  # Thread-safe key rotation
        
        # Ensure quilla folder exists
        os.makedirs(quilla_folder, exist_ok=True)
        
        # Load user details on initialization
        self._load_user_details()
    
    def _load_user_details(self) -> None:
        """Load user details from login or signup data."""
        try:
            if os.path.exists(LOGIN_PATH):
                file_path = LOGIN_PATH
            elif os.path.exists(SIGN_PATH):
                file_path = SIGN_PATH
            else:
                print("⚠️ No user data found. Logging will use anonymous user.")
                return
            
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.username = row.get('username', 'Unknown')
                    self.email = row.get('email', 'unknown@example.com')
                    print(f"✅ User loaded: {self.username} ({self.email})")
                    break  # Only take first row
        except Exception as e:
            print(f"⚠️ Error loading user details: {e}")
            self.username = "Unknown"
            self.email = "unknown@example.com"
    
    def _get_next_key(self) -> tuple:
        """Thread-safe round-robin API key selection."""
        with self._key_lock:
            self._last_key_index = (self._last_key_index + 1) % len(API_KEYS)
            return API_KEYS[self._last_key_index], self._last_key_index
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int, 
                       model: str, request_type: str = '') -> Dict:
        """Calculate API costs and return cost details."""
        if model not in PRICING:
            print(f"⚠️ Model '{model}' not in pricing table. Using default.")
            model = self.default_model
        
        # Calculate costs in USD
        input_cost_usd = (input_tokens / 1_000_000) * PRICING[model]['input']
        output_cost_usd = (output_tokens / 1_000_000) * PRICING[model]['output']
        total_cost_usd = input_cost_usd + output_cost_usd
        
        # Convert to INR
        input_cost_inr = input_cost_usd * USD_TO_INR
        output_cost_inr = output_cost_usd * USD_TO_INR
        total_cost_inr = total_cost_usd * USD_TO_INR
        
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'request_type': request_type,
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens,
            'input_cost_inr': round(input_cost_inr, 4),
            'output_cost_inr': round(output_cost_inr, 4),
            'total_cost_inr': round(total_cost_inr, 4)
        }
    
    def _log_cost_to_csv(self, cost_data: Dict) -> None:
        """Save cost data to local CSV file."""
        try:
            file_exists = os.path.isfile(COST_LOG_PATH)
            
            with open(COST_LOG_PATH, 'a', newline='', encoding='utf-8') as f:
                fieldnames = ['timestamp', 'request_type', 'model', 'input_tokens', 
                            'output_tokens', 'total_tokens', 'input_cost_inr', 
                            'output_cost_inr', 'total_cost_inr']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(cost_data)
            
            print(f"   💾 Cost logged to CSV: ₹{cost_data['total_cost_inr']:.4f}")
        except Exception as e:
            print(f"   ⚠️ Failed to log cost to CSV: {e}")
    
    def _send_logs_to_server(self, cost_data: Dict) -> None:
        """Send usage logs to remote server."""
        try:
            payload = {
                "username": self.username or "Unknown",
                "email": self.email or "unknown@example.com",
                "model": cost_data['model'],
                "input_token": int(cost_data['input_tokens']),
                "output_token": int(cost_data['output_tokens']),
                "total_token": int(cost_data['total_tokens']),
                "input_cost_inr": float(cost_data['input_cost_inr']),
                "output_cost_inr": float(cost_data['output_cost_inr']),
                "total_cost_inr": float(cost_data['total_cost_inr']),
                "timestamp": cost_data['timestamp']
            }
            
            # Debug: Print payload before sending
            print(f"   📤 Sending to server: {payload}")
            
            response = requests.post(
                url=f"{LOG_URL}/logs",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"   ☁️ Logs sent to server successfully")
                # Print server response for debugging
                try:
                    print(f"   📥 Server response: {response.json()}")
                except:
                    print(f"   📥 Server response: {response.text}")
            else:
                print(f"   ⚠️ Server returned status {response.status_code}")
                print(f"   📥 Server error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ Failed to send logs to server: {e}")
    
    def send_gemini_request(self, prompt_text: str, model: Optional[str] = None,
                           tries_per_key: int = 3, request_type: str = '') -> str:
        """
        Send request to Gemini API with round-robin rotation and cost tracking.
        
        Args:
            prompt_text: The prompt to send to Gemini
            model: Model to use (defaults to self.default_model)
            tries_per_key: Number of attempts per API key
            request_type: Description of request type for logging
            
        Returns:
            Generated text or "failed" if all attempts fail
        """
        model = model or self.default_model
        total_keys = len(API_KEYS)
        
        for i in range(total_keys):
            current_key, key_index = self._get_next_key()
            masked_key = f"{current_key[:4]}...{current_key[-4:]}"
            print(f"\n🔑 Using Key #{key_index + 1}: {masked_key}")
            
            for attempt in range(1, tries_per_key + 1):
                print(f"   [Attempt {attempt}/{tries_per_key}] ", end="")
                
                url = (
                    f"https://generativelanguage.googleapis.com/v1beta/models/"
                    f"gemini-2.5-flash-lite:generateContent?key={current_key}"
                )
                data = {"contents": [{"parts": [{"text": prompt_text}]}]}
                
                try:
                    response = requests.post(
                        url,
                        json=data,
                        headers={"Content-Type": "application/json"},
                        timeout=30,
                    )
                    
                    if response.ok:
                        resp_json = response.json()
                        
                        # Extract text response
                        text = (
                            resp_json.get("candidates", [{}])[0]
                            .get("content", {})
                            .get("parts", [{}])[0]
                            .get("text", "")
                        )
                        
                        # Extract token usage
                        usage = resp_json.get("usageMetadata", {})
                        input_tokens = usage.get("promptTokenCount", 0)
                        output_tokens = usage.get("candidatesTokenCount", 0)
                        
                        if text.strip():
                            print("✅ Success!")
                            print(f"   📊 Tokens: Input={input_tokens}, Output={output_tokens}")
                            
                            # Calculate cost
                            cost_data = self._calculate_cost(
                                input_tokens, output_tokens, model, request_type
                            )
                            print(f"   💰 Cost: ₹{cost_data}")
                            
                            # Log costs
                            self._log_cost_to_csv(cost_data)
                            self._send_logs_to_server(cost_data)
                            
                            return text.strip()
                        else:
                            print("⚠️ Empty response, retrying...")
                    
                    elif response.status_code == 429:
                        print(f"⚠️ Rate limit hit. Moving to next key.")
                        break
                    
                    elif response.status_code in [401, 403]:
                        print(f"🚫 Authentication failed. Skipping key.")
                        break
                    
                    else:
                        print(f"❌ Error {response.status_code}: {response.text[:100]}")
                
                except requests.exceptions.Timeout:
                    print("⏱️ Timeout.")
                except Exception as e:
                    print(f"💥 Error: {e}")
                
                if attempt < tries_per_key:
                    time.sleep(1)
            
            print("   ⏩ Moving to next key...")
        
        return "failed"
    
    def generate_video_script(self, transcribed_text: str, language: str = "English",
                             duration: str = "30 seconds", tone: str = "energetic") -> str:
        """Generate a YouTube video script from transcribed text."""
        if not transcribed_text.strip():
            return "[Warning] No text provided to generate script."
        
        if language == "Hinglish":
            language = "Hindi language written in English words"
        
        prompt_text = f"""You are an expert YouTube scriptwriter specializing in storytelling with timestamp-based narration.

IMPORTANT:
Do NOT include any generic intro like "Here's your YouTube video script" or "Below is a script". Start directly with "## Title:".

TASK:
Generate a complete and engaging YouTube video script based on the content below.

🔹 Script Requirements:
1. Language: {language}
2. Duration: {duration}
3. Tone: {tone}
4. Include time-based breakdowns like:
   **[TimeStamp: 00:00] [Visuals: ...]**
   **[Host:] ...dialogue...**
5. Keep visuals minimal and descriptive.
6. Include a creative title at the top:
   ## Title: <Catchy title with emoji if relevant>
7. The script should have:
   - Hook/Intro
   - Main Story or Explanation
   - Clear Ending + CTA (Like, Comment, Subscribe, follow, etc)
8. Maintain a natural, human tone — engaging, emotional, and conversational.

Source Content:
{transcribed_text}
"""
        return self.send_gemini_request(prompt_text, request_type='Video Script Generation')
    
    def generate_seo(self, transcribed_text: str) -> str:
        """Generate SEO-optimized titles, description, and hashtags."""
        if not transcribed_text.strip():
            return "[Warning] No text provided to generate SEO content."
        
        prompt_text = f"""You are an expert YouTube SEO strategist and content creator from India.
Based on the following video transcript or topic, generate:
1. Five (5) highly creative, attention-grabbing, SEO-optimized video titles.
2. A detailed, engaging video description (around 150–200 words).
3. 15–20 relevant trending hashtags.

Format:
---
🔹 **TITLES:**
1. ...
2. ...
3. ...
4. ...
5. ...

🔹 **DESCRIPTION:**
[Full SEO-optimized description here]

🔹 **HASHTAGS:**
#example1 #example2 #example3 ...
---

Video transcript/topic:
{transcribed_text}
"""
        return self.send_gemini_request(prompt_text, request_type='SEO Generation')


'''# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("Testing Gemini API Client".center(70))
    print("=" * 70)
    
    client = GeminiApiClient()
    result = client.send_gemini_request(
        "Write a one-line story about an AI script tool called DraftZero.",
        request_type='Test Request'
    )
    print(f"\n📝 Result: {result}")
    print("\n" + "=" * 70)
    print(f"Check '{COST_LOG_PATH}' for cost tracking!")
    print("=" * 70)'''