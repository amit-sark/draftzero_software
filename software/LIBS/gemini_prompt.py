import requests
import time
import requests

def generate_video_script(transcribed_text, language="English", duration="30 seconds", tone="energetic"):
    import requests

    API_KEY = "AIzaSyD_TAcUoafTPJoUr0jqN-SUZkvFRUC5Fk4"

    if language == "Hinglish":
        language = "Hindi language written in English words"

    if not transcribed_text.strip():
        return "[Warning] No text provided to generate script."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

    # 🎬 Professional prompt for cinematic timestamped YouTube script
    prompt_text = f"""
        You are an expert YouTube scriptwriter specializing storytelling with timestamp-based narration.

        🎯 TASK:
        Generate a complete and engaging YouTube video script based on the content below.

        🔹 Script Requirements:
        1. Language: {language}
        2. Duration: {duration}
        3. Tone: {tone}
        4. Include time-based breakdowns like this:
        **[TimeStamp: 00:00] [Visuals: ...]**
        **[Host:] ...dialogue...**
        5. Keep visuals minimal and descriptive .
        6. Include a creative title at the top in this format:
        ## Title: <Catchy title with emoji if relevant>
        7. The script should have:
        - Hook/Intro
        - Main Story or Explanation
        - Clear Ending + CTA (Like, Comment, Subscribe)
        8. Maintain a natural, human tone — engaging, emotional, and conversational.

    
        Source Content:
        {transcribed_text}
        """


    data = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    # 🔁 Retry logic (3 attempts with exponential backoff)
    MAX_RETRIES = 3
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.ok:
                response_json = response.json()
                script = response_json["candidates"][0]["content"]["parts"][0]["text"]
                print(script)
                return script
            else:
                print(f"[Attempt {attempt}] Error: {response.status_code} — {response.text}")
        except requests.exceptions.Timeout:
            print(f"[Attempt {attempt}] Timeout occurred. Retrying...")
        except Exception as e:
            print(f"[Attempt {attempt}] Request failed: {e}")

        if attempt < MAX_RETRIES:
            wait_time = attempt * 2
            print(f"⏳ Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)

    return "[Error] All attempts failed after 3 retries."

def generate_seo(transcribed_text):
    API_KEY = "AIzaSyD_TAcUoafTPJoUr0jqN-SUZkvFRUC5Fk4"

    if not transcribed_text.strip():
        return "[Warning] No text provided to generate SEO content."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

    # 🔥 Strong prompt tuned for SEO-rich and creative YouTube metadata
    prompt_text = f"""
    You are an expert YouTube SEO strategist and content creator from India.
    Based on the following video transcript or topic, generate:
    1. Five (5) highly creative, attention-grabbing, SEO-optimized video titles.
    2. A detailed, engaging video description (around 150–200 words) with keyword density and natural flow.
    3. 15–20 relevant and trending hashtags for better reach and discoverability.

    Make sure:
    - The titles are emotionally appealing, clickable, and optimized for YouTube algorithm.
    - Include relevant keywords from the topic.
    - Do not repeat titles.
    - Maintain the video tone and style.
    - Return the output in this format:
      ---
      🔹 **TITLES:**
      1. ...
      2. ...
      3. ...
      4. ...
      5. ...
      
      🔹 **DESCRIPTION:**
      [Full SEO-optimized description here]

      🔹 **Stay Connected:**
        [Social Media Links Here]

      🔹 **HASHTAGS:**
      #example1 #example2 #example3 ...
      ---

    Video transcript/topic:
    {transcribed_text}
    """

    data = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }

    try:
        response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        if response.ok:
            response_json = response.json()
            script = response_json["candidates"][0]["content"]["parts"][0]["text"]
            print(script)
            return script
        else:
            return f"[Error] Request failed with status {response.status_code}: {response.text}"
    except Exception as e:
        return f"[Error] Request failed: {e}"
