import os
import requests
import time
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()


# DEEPSEEK API
class DeepSeekClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("Key obtain failed")

        self.base_url = "https://api.deepseek.com/chat/completions"
        self.model = "deepseek-chat"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Speed control
        self.last_request_time = 0
        self.min_request_interval = 5.0  # 5-second interval
        self.daily_request_count = 0
        self.daily_reset_time = time.time()

        # Backoff
        self.consecutive_failures = 0
        self.backoff_base = 5.0

    # Send a message to DeepSeek API and get a reply
    def chat(self, prompt: str, temperature: float = 0.7) -> Optional[str]:

        # Delay
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
            "temperature": temperature,
            "top_p": 0.9,
            "stream": False
        }

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            # Processing speed limit
            if response.status_code == 429:
                print("Reached speed limit, wait for 10 seconds ..")
                time.sleep(10)
                # Retry
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )

            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"DeepSeek API call failed: {e}")
            return None

    def get_wordle_suggestion(
            self,
            correct_pos: dict,
            present_letters: dict,
            absent_letters: set,
            used_words: set,
            word_size
    ) -> Optional[str]:


        template = ["_"] * word_size
        for idx, letter in correct_pos.items():
            template[idx] = letter

        context_lines = [
            f"Wordle Game - Word length: {word_size}",
            f"Board: {' '.join(template)}",
            "Rules:",
            "1. Keep green letters at their positions",
        ]

        if present_letters:
            for letter, bad_positions in present_letters.items():
                context_lines.append(f"2. Include letter '{letter}' but NOT at positions {list(bad_positions)}")
        if absent_letters:
            context_lines.append(f"3. Do NOT use these letters: {', '.join(sorted(absent_letters))}")
        if used_words:
            context_lines.append(f"4. Already guessed words (do not repeat): {', '.join(sorted(used_words))}")
        context_lines.append(
            f"5. Return only the {word_size}-letter word, lowercase, no quotes, no explanation.\nWord:")

        context = "\n".join(context_lines)


        for retry in range(20):
            suggestion = self.chat(context, temperature=0.1 + 0.2 * retry)
            if not suggestion:
                continue

            word = suggestion.strip().lower()

            if self._is_valid_word(word, correct_pos, present_letters, absent_letters, used_words, word_size):
                return word

        return None

    # verify words
    def _is_valid_word(self, word, correct_pos, present_letters, absent_letters, used_words, word_size):

        if len(word) != word_size or word in used_words:
            return False

        # verify correct
        for idx, letter in correct_pos.items():
            if word[idx] != letter:
                return False

        # verify exist but wrong place
        for letter, bad_positions in present_letters.items():
            if letter not in word:
                return False
            for pos in bad_positions:
                if word[pos - 1] == letter:  # 注意：bad_positions 是从1开始的
                    return False

        # verify not exist
        for letter in absent_letters:

            if letter not in correct_pos.values() and letter not in present_letters and letter in word:
                return False

        return True


