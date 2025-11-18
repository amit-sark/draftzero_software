
def youtube(platform,language,duration,tone,transcribed_text,next_part='no'):

    if next_part.upper()=="NO":
        prompt_text = f"""You are an expert {platform} scriptwriter specializing in storytelling with timestamp-based narration.
        IMPORTANT:
        Do NOT include any generic intro like "Here's your {platform} video script" or "Below is a script". Start directly with "## Title:".
        TASK:
        Generate a complete and engaging {platform} video script based on the content below.
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
        return prompt_text
    else :
        prompt_text = f"""
            You are an expert {platform} scriptwriter specializing in storytelling with timestamp-based narration.
            IMPORTANT:
            Do NOT include any generic intro like "Here's your {platform} video script". 
            Start directly with "## Title:".
            TASK:
            Generate a complete and engaging {platform} video script based on the content below.
            {transcribed_text}
            🔹 Script Requirements:
            1. Language: {language}
            2. Duration: {duration}
            3. Tone: {tone}
            4. Include time-based breakdowns like:
            [TimeStamp: 00:00] [Visuals: ...]
            [Host:] ...dialogue...
            5. Keep visuals minimal and descriptive.
            6. Start with:
            ## Title: <Catchy title with emoji if relevant>
            7. Script Structure:
            - Hook / Intro
            - Main Story / Explanation
            - Ending + CTA (Like, Comment, Subscribe)
            8. Maintain a human, emotional, conversational tone.
            📄 Source Content:
            {transcribed_text}
            """

        return prompt_text


def instagram(platform, language, duration, tone, transcribed_text,next_part='no'):
    print(next_part.upper())

    if next_part.upper()=="NO":
        prompt_text = f"""
        You are an expert {platform} Reels scriptwriter specializing in short-form, fast-paced storytelling.

        IMPORTANT:
        Start directly with "## Title:".

        TASK:
        Generate a punchy, high-retention {platform} Reel script using the content below.

        🔹 Script Requirements:
        1. Language: {language}
        2. Duration: {duration} (Reel-style: short, crisp, high retention)
        3. Tone: {tone}
        4. Use compact timestamps like:
        [00:00] Hook
        [00:03] Visuals + Dialogue
        5. Keep visuals minimal but energetic.
        6. Start with:
        ## Title: <Short, catchy, emoji-friendly title>
        7. Structure:
        - Strong Hook (first 2 seconds 🔥)
        - Short narrative / explanation
        - CTA: Follow / Like / Save
        8. Maintain a high-energy, conversational tone.
        9. Include multiple host/dialogue formats.

        Source Content:
        {transcribed_text}
        """
        print("Sending instagram prompt .....")
        return prompt_text
    else:
        continuation_text = f"""
            🔄 CONTINUATION INSTRUCTION:
            This Reel is PART OF A SERIES.

            Use the previous part summary to continue the story smoothly and maintain fast-paced flow.

            Previous Part Summary:
            {transcribed_text}

            Ensure that you:
            - Continue the narrative without repeating the previous part
            - Keep the pacing tight and energetic
            - Maintain character behavior and plot consistency
            - Add a punchy twist or new reveal for retention
            - End with a hook leading to the next part
            """
                
        prompt_text = f"""
            You are an expert {platform} Reels scriptwriter specializing in short-form, fast-paced storytelling.

            IMPORTANT:
            Start directly with:
            ## Title: <Catchy Title with emojis>

            TASK:
            Generate a punchy, high-retention {platform} Reel script using the content below.

            {continuation_text}

            🔹 Script Requirements:
            1. Language: {language}
            2. Duration: {duration} (Reel-style: short, crisp, high retention)
            3. Tone: {tone}
            4. Use compact timestamps like:
            [00:00] Hook
            [00:03] Visuals + Dialogue
            5. Keep visuals minimal but energetic.
            6. Structure:
            - 🔥 Strong Hook (first 2 seconds)
            - Short narrative or explanation
            - High engagement moments
            - CTA: Follow / Like / Save
            7. Maintain a high-energy, conversational tone.
            8. Include multiple hosts/dialogue formats.

            📄 Source Content:
            {transcribed_text}
            """
        return prompt_text

def micro_drama(platform, language, duration, tone, transcribed_text,next_part="no"):

    if next_part.upper()=="NO":
        prompt_text = f"""
        You are an expert Micro-Drama writer specializing in cinematic, emotional short stories.

        IMPORTANT:
        Start directly with:
        ## Title: <Short, emotional, cinematic title>

        CHARACTER HANDLING:
        • Automatically detect characters from the source content.  
        • If names are missing, infer natural names/roles (e.g., “Arjun”, “Mira”, “Stranger”, “Mother”, “Boss”).  
        • Keep character list minimal and integrate it naturally in the story beginning, not as a formatted block.

        GUIDELINES:
        1. Language: {language}
        2. Duration: {duration}
        3. Tone: {tone}
        4. Simple formatting only (no loglines, big headers, bold blocks, etc).
        5. Use timestamps like:
        **[TimeStamp: 00:00] [Visuals: ...]**
        **[Host:] ...dialogue...**
        6. Use real, natural dialogue with emotional beats.
        7. End with a soft CTA: Follow for more micro-dramas.

        #
        Source Content:
        {transcribed_text}
        """
        return prompt_text

    else: 
        continuation_text = f"""
            🔄 CONTINUATION INSTRUCTION:
            This micro-drama is PART OF A SEQUENCE.

            Use the previous part summary to continue the story, maintain emotional flow, character consistency, and narrative tension.

            Previous Part Summary:
            {transcribed_text}

            Make sure to:
            - Continue emotional beats
            - Maintain character personalities and dynamics
            - Build on unresolved conflict
            - Add a twist, reveal, or escalation
            - End with a cliffhanger or emotional punch
            """
        prompt_text = f"""
        You are an expert Micro-Drama writer specializing in cinematic, emotional short stories.

        IMPORTANT:
        Start directly with:
        ## Title: <Short, emotional, cinematic title>

        
        TASK:
            Write a complete, engaging Micro-Drama episode script based on the content below.
            {continuation_text}


        CHARACTER HANDLING:
        • Automatically detect characters from the source content.  
        • If names are missing, infer natural names/roles (e.g., “Arjun”, “Mira”, “Stranger”, “Mother”, “Boss”).  
        • Keep character list minimal and integrate it naturally in the story beginning, not as a formatted block.

        GUIDELINES:
        1. Language: {language}
        2. Duration: {duration}
        3. Tone: {tone}
        4. Simple formatting only (no loglines, big headers, bold blocks, etc).
        5. Use timestamps like:
        **[TimeStamp: 00:00] [Visuals: ...]**
        **[Host:] ...dialogue...**
        6. Use real, natural dialogue with emotional beats.
        7. End with a soft CTA: Follow for more micro-dramas.

        Source Content:
        {transcribed_text}
        """
        return prompt_text


def webseries(platform, language, episode_duration, tone, transcribed_text,next_part='no'):

    if next_part.upper()=="NO":
        prompt_text = f"""
        You are an expert {platform} Scriptwriter specializing in cinematic, episodic storytelling with rich characters and scene-based narration.

        IMPORTANT:
        Start directly with:
        ## Title: <Cinematic Web-Series Episode Title>

        TASK:
        Write a complete, engaging Web-Series episode script based on the content below.

        🎬 Web-Series Script Should Full-Fill The Requirements:
        1. Language: {language}
        2. Episode Duration: {episode_duration}
        3. Tone: {tone} 
        4. Format the script with clear scene sections like:
        **[TimeStamp: 00:00] [Visuals: ...]**
        **[Character A]: dialogue...**
        5. Use rich visuals but NOT too technical.
        6. Include:
        • Opening Hook (strong first scene)
        • Character introductions
        • Conflict development
        • Emotional or action beats
        • End-of-episode cliffhanger or twist
        7. Allow multiple characters and natural dialogues.
        8. Maintain pacing suitable for a web-series:
        • Short scenes
        • High engagement
        • Emotional depth
        9. Script Elements Should Include:
        - Character names
        - Scene transitions
        - Background mood / ambience
        - Key turning points
        10. Episode should feel like part of a larger story arc.
        11. End with a subtle CTA: “Follow for Episode 2”.

        📄 Source Material to Adapt:
        {transcribed_text}
        """
        return prompt_text
    else:
        continuation_text = f"""
            🔄 CONTINUATION INSTRUCTION:
            This is NOT the first episode. Continue the story from the previous episode summary below.

            Previous Episode Summary:
            {transcribed_text}

            Ensure that:
            - Characters remain consistent
            - Ongoing story arcs continue naturally
            - Previous conflicts and mysteries are not repeated, but built upon
            - New obstacles, twists, or emotional turns are added
            - The pacing remains episodic and cinematic
            - End with a strong cliffhanger leading to the next episode
            """
                
        prompt_text = f"""
            You are an expert {platform} Scriptwriter specializing in cinematic, episodic storytelling with rich characters and scene-based narration.

            IMPORTANT:
            Start directly with:
            ## Title: <Cinematic Web-Series Episode Title>

            TASK:
            Write a complete, engaging Web-Series episode script based on the content below.

            {continuation_text}

            🎬 Web-Series Script Should Full-Fill The Requirements:
            1. Language: {language}
            2. Episode Duration: {episode_duration}
            3. Tone: {tone} 
            4. Format the script with clear scene sections such as:
            **[TimeStamp: 00:00] [Visuals: ...]**
            **[Character A]: dialogue...**
            5. Use rich visuals but NOT overly technical.
            6. Include:
            • Opening Hook (first scene must grab attention)
            • Character introductions or re-entry
            • Conflict development
            • Emotional or action beats
            • End-of-episode cliffhanger or twist
            7. Allow multiple characters and natural dialogues.
            8. Maintain pacing suitable for a web-series:
            • Short, cinematic scenes
            • Strong engagement
            • Emotional depth
            9. Script elements must include:
            - Character names
            - Scene transitions
            - Background mood / ambience
            - Key turning points
            10. Ensure the episode feels like part of a larger story arc.
            11. End with a subtle CTA: “Follow for Episode 2” or similar.

            📄 Source Material to Adapt:
            {transcribed_text}
            """
        return prompt_text

def custom_platform(platform, language, duration, tone, transcribed_text, next_part='no'):
    """
    Universal script generator for any custom platform.
    
    Parameters:
    -----------
    platform : str
        The name of the platform (e.g., "TikTok", "LinkedIn", "Twitter", "Podcast")
    language : str
        Target language for the script
    duration : str
        Duration of the content (e.g., "30 seconds", "5 minutes")
    tone : str
        Tone of the content (e.g., "Professional", "Casual", "Humorous")
    transcribed_text : str
        Source content to base the script on
    next_part : str, optional
        Whether this is a continuation ("yes"/"no")
    
    Returns:
    --------
    str : The generated prompt text
    """
    
    if next_part.upper() == "NO":
        prompt_text = f"""You are an expert {platform} content creator and scriptwriter specializing in engaging storytelling.

            IMPORTANT:
            Do NOT include any generic intro like "Here's your {platform} script" or "Below is the content".
            Start directly with "## Title:".

            TASK:
            Generate a complete and engaging {platform} script based on the content below.

            🔹 Script Requirements:
            1. Language: {language}
            2. Duration: {duration}
            3. Tone: {tone}
            4. Platform: {platform} (Optimize for {platform}'s audience and typical format)
            5. Include appropriate formatting for {platform}:
            - Use timestamps, scenes, or sections as needed
            - Add visual descriptions if relevant
            - Include dialogue or narration as appropriate
            6. Start with:
            ## Title: <Catchy, platform-appropriate title with emoji if relevant>
            7. Script Structure should include:
            - Strong Hook/Opening
            - Main Content/Story/Message
            - Clear Ending
            - Call-to-Action (Follow, Like, Subscribe, etc.) appropriate for {platform}
            8. Maintain a natural, human tone — engaging, emotional, and conversational.
            9. Adapt the style to match typical {platform} content patterns.

            📄 Source Content:
            {transcribed_text}
            """
    else:
        prompt_text = f"""You are an expert {platform} content creator and scriptwriter specializing in engaging storytelling.

    IMPORTANT:
    Do NOT include any generic intro like "Here's your {platform} script".
    Start directly with "## Title:".

    🔄 CONTINUATION INSTRUCTION:
    This is PART OF A SERIES on {platform}.
    Use the previous part summary below to continue the story smoothly.

    Previous Part Summary:
    {transcribed_text}

    Ensure that you:
    - Continue the narrative without repeating the previous part
    - Maintain consistent pacing and style for {platform}
    - Keep character behavior and plot consistency (if applicable)
    - Add new value, insights, or story progression
    - End with a hook leading to the next part

    TASK:
    Generate a continuation script for {platform} based on the content above.

    🔹 Script Requirements:
    1. Language: {language}
    2. Duration: {duration}
    3. Tone: {tone}
    4. Platform: {platform} (Optimize for {platform}'s audience and typical format)
    5. Include appropriate formatting for {platform}:
    - Use timestamps, scenes, or sections as needed
    - Add visual descriptions if relevant
    - Include dialogue or narration as appropriate
    6. Start with:
    ## Title: <Catchy, platform-appropriate title with emoji if relevant>
    7. Script Structure should include:
    - Strong Hook/Opening (that connects to previous part)
    - Main Content/Story/Message
    - Clear Ending or Cliffhanger
    - Call-to-Action appropriate for {platform}
    8. Maintain a natural, human tone — engaging, emotional, and conversational.
    9. Adapt the style to match typical {platform} content patterns.

    📄 Source Content:
    {transcribed_text}
    """
        
    return prompt_text