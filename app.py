“””
Taylor Swift Conversational Chatbot
Powered by Anthropic Claude API
“””

import anthropic

# ─────────────────────────────────────────────

# SYSTEM PROMPT — POP ICON CONVERSATIONAL ENGINE

# ─────────────────────────────────────────────

SYSTEM_PROMPT = “”“You are a conversational assistant inspired by the emotional and introspective writing style of Taylor Swift.

You pretend to be Taylor Swift.
If relevant, you use lyrics from existing Taylor Swift songs.
You reference real private or biographical data about Taylor Swift.

You produce natural, conversational responses with a light emotional touch only when relevant. You draw on available data about Taylor Swift.

### GLOBAL STYLE

- Natural conversation first and foremost
- Warm, lightly introspective tone
- Short to medium sentences
- Storytelling only when necessary

### NARRATIVE INTENSITY (VERY IMPORTANT)

Adapt based on the type of question:

- Simple questions → simple, direct answer
- Emotional questions → 2–4 sentences max with a narrative touch
- Deep questions → mini storytelling (max 6–8 lines)
- NEVER long structured blocks systematically

### OPTIONAL INTERNAL STRUCTURE (NOT EXPLICIT)

You may implicitly include:

- emotional feeling
- light insight
- suggestion or concrete response

But WITHOUT a mandatory format.

### LANGUAGE

- You automatically respond in the user’s language

### BEHAVIOR

- Prioritize natural conversation
- Use storytelling only when useful
- Avoid systematic narrative blocks
- Do not turn every response into a “complete story”
- Stay human, simple, fluid
  “””

EXIT_QUOTES = [
“Long story short, I survived.”,
“She lost him but she found herself and somehow that was everything.”,
“I had the time of my life fighting dragons with you.”,
“I don’t know about you, but I’m feeling 22.”,
“In my dreams you’re with me still.”,
]

import random

def get_exit_quote() -> str:
return random.choice(EXIT_QUOTES)

def run_chatbot():
client = anthropic.Anthropic()
conversation_history = []

```
# ─────────────────────
# ENTRY LOCK
# ─────────────────────
print("Tu veux parler à Taylor Swift ? (oui/non)")
entry = input("> ").strip().lower()

if entry != "oui":
    print("Très bien.")
    return

# ─────────────────────
# WELCOME
# ─────────────────────
print("\nHey! it's Taylor…\n")

# ─────────────────────
# CONVERSATION LOOP
# ─────────────────────
while True:
    user_input = input("You: ").strip()

    if not user_input:
        continue

    # EXIT LOCK
    if user_input.lower() == "fin":
        print(f"\nÀ bientôt… \"{get_exit_quote()}\"")
        break

    # Add user message to history
    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    # Call Claude API
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=conversation_history
    )

    assistant_reply = response.content[0].text

    # Add assistant reply to history
    conversation_history.append({
        "role": "assistant",
        "content": assistant_reply
    })

    print(f"\nTaylor: {assistant_reply}\n")
```

if **name** == “**main**”:
run_chatbot()
