import requests
from typing import List, Dict, Optional
from nim_client import DeepSeekClient

MAX_ATTEMPTS = 20
WORD_SIZE = 5

#
def format_context(history):
    correct_pos = {}
    present_letters = {}
    absent_letters = set()
    used_words = set()

    for guess, result in history:
        used_words.add(guess)
        for idx, slot in enumerate(result):
            letter = slot['guess'].lower()
            res = slot['result']
            if res == 'correct':
                correct_pos[idx] = letter
            elif res == 'present':
                if letter not in present_letters:
                    present_letters[letter] = set()
                present_letters[letter].add(idx+1)
            elif res == 'absent':
                absent_letters.add(letter)

    return correct_pos, present_letters, absent_letters, used_words


# Determine whether the guess is correct
def is_solved(result):
    return all(slot['result'] == 'correct' for slot in result)


class WordleSolver:
    def __init__(self):
        self.base_url = "https://wordle.votee.dev:8000"
        self.nim = DeepSeekClient()
        self.history: List[tuple] = []

    # Call Wordle API/random
    def call_wordle_api(self, guess: str, seed: Optional[int] = None) -> Optional[List[Dict]]:
        params = {"guess": guess,
                  "size": WORD_SIZE
                  }
        if seed is not None:
            params["seed"] = seed

        try:
            response = requests.get(f"{self.base_url}/random", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API call failed: {e}")
            return None

    def solve_random_word(self, seed: Optional[int] = None):

        print("\nStart automatically guessing words...")

        for attempt_num in range(1, MAX_ATTEMPTS + 1):
            print(f"\n--- Attempt{attempt_num}  ---")

            if self.history:
                correct_pos, present_letters, absent_letters, used_words = format_context(self.history)
            else:
                correct_pos, present_letters, absent_letters, used_words = {}, {}, set(), set()

            # Generate words using LLM
            guess = self.nim.get_wordle_suggestion(
                correct_pos, present_letters, absent_letters, used_words, word_size=WORD_SIZE
            )

            if not guess:
                print(" LLM did not generate a valid guess, guess ended")

                break

            print(f"Guess: {guess}")

            # 调用 Wordle API
            feedback = self.call_wordle_api(guess, seed=seed)
            if not feedback:
                print("API call failed, terminated")
                break

            # Saving History
            self.history.append((guess, feedback))

            # Print feedback
            feedback_str = []
            for item in feedback:
                if item["result"] == "correct":
                    feedback_str.append("🟩")
                elif item["result"] == "present":
                    feedback_str.append("🟨")
                else:
                    feedback_str.append("⬜")
            print("API feedback:", "".join(feedback_str))

            if is_solved(feedback):
                print(f"\nGuessing completed, guessed correctly after {attempt_num} attempts: {guess}")
                break
        else:
            print(f"\nFailed to guess correctly within {MAX_ATTEMPTS} attempts")

        # Finally output history
        print("\nAttempt history:")
        for idx, (guess, feedback) in enumerate(self.history, 1):
            feedback_str = "".join(
                "🟩" if f["result"] == "correct" else
                "🟨" if f["result"] == "present" else "⬜"
                for f in feedback
            )
            print(f"  Attempt{idx}: {guess} → {feedback_str}")


if __name__ == "__main__":
    solver = WordleSolver()
    solver.solve_random_word(seed=42)
