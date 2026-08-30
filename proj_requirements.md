# GreenTech - Project Requirements

## 1. PROJECT OVERVIEW

Project Name:

GreenTech

Problem Statement:

ID: I-NXS-010
Problem: Multilingual AI Farmer Advisory Assistant
Theme: Software
Category: Generative AI & AgriTech

Expected Output:

An AI advisory assistant with:
- multilingual conversational interface
- agricultural knowledge layer
- voice interaction
- recommendation workflow

GreenTech must be a REAL, WORKING application.

The goal is not to build the largest application.

The goal is to build a simple, reliable and meaningful agricultural AI assistant that demonstrates:

1. Natural-language understanding
2. Multilingual interaction
3. Voice input
4. Agricultural reasoning
5. Useful recommendations
6. Clean user experience
7. Proper AI/API integration

Prioritize working functionality over unnecessary features.

---

# 2. IMPORTANT SCOPE RULE

This project is being built completely from scratch.

GreenTech must be independent.

DO NOT:

- use Agri-ai
- use KrishiSaarthi
- import code from previous projects
- depend on previous project folders
- depend on previous virtual environments
- copy previous broken implementations
- assume previous dependencies are installed
- assume previous APIs or SDKs are correct

Everything required for GreenTech must exist inside the GreenTech project root.

---

# 3. CORE USER EXPERIENCE

The application should have one clear workflow:

Farmer
↓
Select language
↓
Enter crop/problem using text OR voice
↓
Convert voice to text if voice is used
↓
Send natural-language problem to Gemini
↓
Gemini uses agricultural knowledge/context
↓
Generate practical recommendation
↓
Display answer in the selected language
↓
Optionally read the answer aloud

The entire workflow must actually work.

Do not add unnecessary features that make this core workflow unreliable.

---

# 4. INPUT METHODS

GreenTech must support two primary input methods:

## TEXT INPUT

The farmer can type a normal natural-language description.

Example:

"My paddy leaves are becoming yellow and the plants are not growing properly."

Other examples:

"My rice crop is looking weak."

"The lower leaves of my paddy are turning yellow."

"My tomato plants have started developing spots."

The farmer must NOT be required to use a specific sentence format.

---

## VOICE INPUT

The farmer can press a microphone/record button and speak naturally.

Example:

"My rice leaves are turning yellow. What should I do?"

The system should:

1. Record microphone audio.
2. Process the audio.
3. Transcribe it using Faster-Whisper.
4. Display the transcript.
5. Allow the farmer to edit the transcript.
6. Send the final text to the AI.
7. Display the agricultural recommendation.

If voice fails, text input must continue working.

---

# 5. MULTILINGUAL SUPPORT

The application must support:

- English
- Telugu
- Hindi
- Tamil
- Kannada

The selected language should affect:

1. Voice transcription where supported.
2. AI response language.
3. User-facing agricultural recommendations.

Example:

User selects:

Telugu

Speaks or types a farming problem.

GreenTech should return the agricultural recommendation in Telugu.

Do not require the farmer to translate their problem manually.

---

# 6. VOICE ARCHITECTURE

Use:

Microphone
→ Audio recording
→ Valid audio format
→ Faster-Whisper
→ Text transcript
→ Gemini
→ Agricultural recommendation

Use a multilingual Faster-Whisper model.

Do NOT use an English-only model.

Before implementation, verify:

- microphone recording library
- supported audio format
- Faster-Whisper compatibility
- model compatibility
- FFmpeg requirement
- Windows compatibility

Do not assume FFmpeg is installed.

If FFmpeg is actually required:

- detect it
- show a clear setup message if missing
- do not silently fail
- do not crash the entire application

---

# 7. VOICE ERROR HANDLING

Handle:

- microphone unavailable
- microphone permission failure
- recording failure
- invalid audio
- unsupported audio format
- FFmpeg unavailable
- Faster-Whisper unavailable
- model download failure
- transcription failure
- empty transcription

The user should receive a simple understandable message.

Do NOT show raw Python tracebacks in the application.

---

# 8. GEMINI AI

Use Google Gemini as the main AI reasoning system.

Use the CURRENT official Google GenAI Python SDK.

DO NOT use:

google-generativeai

Do not copy old Gemini API tutorials without verifying them.

Before implementation:

1. Verify the current official Google GenAI SDK.
2. Verify currently available Gemini models.
3. Select an appropriate currently supported model.
4. Prefer a model suitable for development/testing and available on the intended free/development tier.
5. Keep the model name centralized in configuration.

Do not scatter model names throughout the code.

---

# 9. API KEY SECURITY

Use:

.env

The Gemini API key must NEVER be:

- hardcoded
- displayed
- printed
- logged
- committed
- returned to the UI

Create:

.env.example

Example:

GEMINI_API_KEY=
GEMINI_MODEL=

Add:

.env

to:

.gitignore

The application may show:

Gemini API: Configured

or:

Gemini API: Not configured

Never show the actual key.

---

# 10. AGRICULTURAL KNOWLEDGE LAYER

GreenTech should contain a small local agricultural knowledge layer.

Example:

data/agriculture.json

This can contain useful information for common crops such as:

- rice
- paddy
- tomato
- cotton
- chilli
- maize
- wheat
- groundnut
- banana
- mango

The local data may contain:

- crop information
- common problems
- common diseases
- nutrient issues
- basic growing conditions
- basic preventive practices

IMPORTANT:

The local dataset is SUPPORTING KNOWLEDGE.

It must NOT restrict the application.

If a farmer enters a crop that does not exist in agriculture.json:

DO NOT reject the crop.

Send the crop and problem to Gemini.

Gemini should still attempt to provide a useful response.

---

# 11. NATURAL LANGUAGE REASONING

DO NOT use keyword-based diagnosis.

NEVER build the main diagnosis using code such as:

if "yellow leaves" in text:
    return ...

Do not create separate hardcoded answers for individual phrases.

The AI must understand natural language.

For example, these should all be treated as meaningful agricultural descriptions:

"My rice leaves are yellow."

"My paddy leaves have started losing their green colour."

"The lower leaves are becoming yellow."

"My rice crop looks weak and yellow."

"Why are my paddy plants turning yellow?"

The LLM should perform the reasoning.

The application should provide agricultural knowledge/context to the LLM where useful.

---

# 12. AI RECOMMENDATION WORKFLOW

The AI should receive:

- crop name
- farmer's problem description
- selected language
- relevant local agricultural knowledge, if available

The AI should produce a practical advisory response.

Recommended structure:

## Problem Summary

Briefly explain what the farmer appears to be experiencing.

## Possible Causes

List likely causes.

## What to Check

Give practical observations the farmer can make.

## Recommended Actions

Give clear and practical steps.

## What to Avoid

Mention actions that could worsen the problem.

## Prevention

Give basic preventive guidance.

## When to Contact an Expert

Explain when professional agricultural assistance may be needed.

The AI must distinguish between:

- known information
- possible causes
- recommendations

Do not claim certainty when the available information is insufficient.

Use language such as:

"Possible cause"

"One possibility"

"Based on the information provided"

when appropriate.

---

# 13. AI SERVICE

Keep Gemini API logic separate from the UI.

Create:

services/ai_service.py

This service should handle:

- Gemini initialization
- model configuration
- prompt construction
- agricultural context
- AI response generation
- API errors
- timeout/errors
- missing API key

The UI must not contain large amounts of Gemini API logic.

---

# 14. VOICE SERVICE

Create a voice service responsible for:

- microphone recording
- audio handling
- Faster-Whisper transcription
- language selection
- error handling
- dependency checks

The UI should call the voice service rather than implementing the complete transcription pipeline itself.

---

# 15. SIMPLE TRANSLATION STRATEGY

Do NOT create a complicated translation architecture unless it is actually necessary.

The primary requirement is that the farmer can interact in:

- English
- Telugu
- Hindi
- Tamil
- Kannada

Use the AI's multilingual capabilities where appropriate.

The system should:

1. Receive the farmer's input.
2. Understand the input language/selected language.
3. Reason about the agricultural problem.
4. Return the recommendation in the selected language.

Avoid unnecessary translation APIs if Gemini can handle the requirement reliably.

---

# 16. TEXT TO SPEECH

Provide a simple:

[ Read Aloud ]

feature for AI responses.

Use an available TTS solution.

For Windows:

- detect available voices
- do not assume every Indian language voice exists
- if the selected language voice is unavailable, show a clear message
- do not crash the application

TTS is secondary.

If TTS is unavailable, the main text/voice-to-AI workflow must still work.

---

# 17. SIMPLE APPLICATION DESIGN

The application should NOT contain 10+ unnecessary pages.

Keep the interface focused.

Recommended sections:

1. Home
2. Farmer Assistant
3. History
4. Settings
5. About

The main screen should focus on the actual assistant.

The user should immediately understand:

"What crop are you having a problem with?"

and:

"Describe your problem using text or voice."

---

# 18. MAIN ASSISTANT UI

Create a clean agricultural AI interface.

Example:

GreenTech

AI Agricultural Assistant

"Describe your crop problem and get practical guidance."

Language:

[ English / తెలుగు / हिन्दी / தமிழ் / ಕನ್ನಡ ]

Crop:

[ Enter crop name... ]

Problem:

[ Describe what is happening to your crop... ]

[ 🎤 Voice ]       [ Get Advice ]

After submission:

AI Agricultural Advice

Problem Summary

Possible Causes

What to Check

Recommended Actions

What to Avoid

Prevention

When to Contact an Agricultural Expert

[ Read Aloud ]

The interface should be clean and easy to understand.

---

# 19. CROP INPUT

Do NOT force the farmer to select from a fixed dropdown.

Use a text input.

Example:

[ Enter crop name... ]

Accept arbitrary crops.

Examples:

rice
paddy
tomato
cotton
chilli
maize
wheat
groundnut
banana
mango

Unknown crops must not cause an error.

---

# 20. HISTORY

Keep a simple history feature.

Store:

- date/time
- crop
- farmer's problem
- AI recommendation
- selected language
- input method

Allow the farmer to view previous advice.

Do not build a complicated database unless necessary.

A simple local JSON/SQLite solution is sufficient.

---

# 21. SETTINGS

Keep Settings simple.

Include:

- response language
- TTS on/off
- Gemini API status
- voice system status
- clear history

NEVER display API keys.

---

# 22. ABOUT

Show:

GreenTech

Multilingual AI Farmer Advisory Assistant

Problem Statement:

I-NXS-010

Theme:

Software

Category:

Generative AI & AgriTech

Briefly explain that GreenTech combines:

- Generative AI
- agricultural knowledge
- multilingual interaction
- voice technology

---

# 23. UI DESIGN

The interface should look clean and professional.

Use:

- dark navy background
- subtle agricultural teal accents
- readable typography
- modern cards
- clean spacing
- subtle borders
- restrained shadows

Color system:

Main background:
#0B1220

Secondary:
#0F172A

Cards:
#111C2E

Elevated cards:
#162238

Borders:
#24344D

Primary text:
#F8FAFC

Secondary text:
#CBD5E1

Muted text:
#94A3B8

Primary accent:
#14B8A6

Secondary accent:
#38BDF8

Warning:
#F59E0B

Success:
#22C55E

Do not make the whole application bright green.

Avoid:

- fluorescent green
- excessive gradients
- childish graphics
- excessive emojis
- giant illustrations
- generic Bootstrap appearance
- unnecessary animations

The design should communicate:

"AI agricultural intelligence"

not:

"green farming website."

---

# 24. PROJECT STRUCTURE

Keep the architecture simple.

Recommended:

GreenTech/
│
├── proj_req.md
├── main.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
│
├── data/
│   └── agriculture.json
│
├── services/
│   ├── ai_service.py
│   ├── voice_service.py
│   └── tts_service.py
│
├── utils/
│   ├── config.py
│   └── storage.py
│
└── assets/

The structure may be changed if there is a genuinely simpler design.

DO NOT create files merely to make the project look sophisticated.

Every file must have a real purpose.

---

# 25. DEPENDENCIES

Create:

requirements.txt

Every Python package actually used must be listed.

Do not install unnecessary packages.

Before selecting a dependency:

- verify that it is maintained/supported
- verify Python compatibility
- verify compatibility with Windows
- verify API compatibility

After adding or removing a package:

UPDATE requirements.txt.

---

# 26. STREAMLIT SAFETY

Use Streamlit carefully.

Initialize session state BEFORE creating widgets.

Do NOT modify a widget-owned session-state key after the widget has been created.

Avoid patterns such as:

st.text_input(..., key="crop")

st.session_state["crop"] = value

after the widget is instantiated.

Prefer:

- widget return values
- callbacks
- separate state keys
- initialization before widget creation

Test the actual application to catch Streamlit runtime errors.

---

# 27. ERROR HANDLING

The application must gracefully handle:

- missing Gemini API key
- invalid Gemini API key
- unavailable Gemini model
- Gemini API failure
- API timeout
- rate limit
- microphone failure
- FFmpeg missing
- Faster-Whisper failure
- transcription failure
- empty input
- TTS failure
- history/storage failure

Never show raw Python tracebacks to farmers.

The application should remain usable when optional services fail.

For example:

If voice fails:

Text input should still work.

If TTS fails:

The AI response should still be displayed.

If Gemini is not configured:

The application should still start and clearly show that AI functionality requires configuration.

Do not fake AI output.

---

# 28. SECURITY

Never:

- hardcode API keys
- expose API keys
- print API keys
- log API keys
- commit .env
- display environment variables

Use:

.env

and:

.env.example

---

# 29. RUNTIME TESTING

IMPORTANT:

Compilation is NOT enough.

This:

python -m py_compile ...

does NOT prove that the application works.

The application must actually be launched with:

streamlit run main.py

Then test the UI.

---

# 30. REQUIRED TESTS

## Startup

Test:

- application starts
- no startup traceback
- UI loads
- navigation works

## Text

Test:

"My rice leaves are turning yellow."

Then test:

"My paddy crop has started losing its green colour."

Then test a completely different wording.

The AI must respond without exact phrase matching.

## Arbitrary crop

Test:

rice

paddy

tomato

cotton

chilli

maize

and at least one crop NOT present in agriculture.json.

Unknown crops must not be rejected.

## Voice

Test:

English voice input.

Then test available supported Indian languages:

Telugu

Hindi

Tamil

Kannada

Verify:

microphone
→ recording
→ transcription
→ editable transcript
→ AI response

## Language

Test each supported language.

Verify that the AI response is returned in the selected language.

## TTS

Test Read Aloud.

If a voice is unavailable, verify that the application reports this cleanly.

## History

Test:

- save
- open
- clear

## API failure

Test the application without GEMINI_API_KEY.

The application must not crash.

---

# 31. DEVELOPMENT PHASES

Do not build everything at once.

## PHASE 1 - FOUNDATION

Create:

- project root
- requirements.txt
- .env.example
- .gitignore
- configuration
- Streamlit application
- clean UI
- language selector
- crop input
- text input
- basic navigation

Run the application.

Fix all startup errors.

---

## PHASE 2 - GEMINI CORE

Implement:

- Gemini service
- current official SDK
- current supported model
- API key configuration
- agricultural context
- natural-language diagnosis
- multilingual response

Test real Gemini requests.

Fix all API errors before continuing.

---

## PHASE 3 - VOICE

Implement:

- microphone recording
- audio handling
- Faster-Whisper
- multilingual transcription
- transcript editing
- error handling

Test the complete microphone → transcript pipeline.

---

## PHASE 4 - TTS

Implement:

- Read Aloud
- Windows voice detection
- graceful unsupported-language handling

---

## PHASE 5 - HISTORY

Implement:

- local history storage
- history viewing
- clearing history

---

## PHASE 6 - FINAL POLISH

Improve:

- spacing
- typography
- cards
- buttons
- sidebar
- error messages
- responsiveness
- visual consistency

Do not add major new features during final polish.

---

# 32. PHASE CONTROL

After EVERY phase:

1. Run the application.
2. Test the implemented feature.
3. Check terminal errors.
4. Check UI errors.
5. Fix the root cause.
6. Re-run the application.
7. Only then move to the next phase.

Do not continue building on top of broken code.

---

# 33. API VERIFICATION RULE

Before implementing Gemini or another external API:

1. Check current official documentation.
2. Verify current SDK.
3. Verify model availability.
4. Verify method signatures.
5. Verify input/output format.
6. Implement.
7. Run a real request.
8. Handle errors.
9. Only then mark the feature complete.

Never blindly rely on old tutorials.

---

# 34. NO FAKE FUNCTIONALITY

The following must NEVER be faked:

- Gemini responses
- voice transcription
- translations
- TTS
- API status

If an external service is unavailable:

show the real unavailable state.

Do not generate fake output simply to make the demo appear functional.

---

# 35. SUCCESS CRITERIA

GreenTech is considered successful when a judge can:

1. Open the application.
2. Select a language.
3. Enter a crop.
4. Type a natural farming problem.
5. Receive an AI-generated agricultural recommendation.
6. Speak the problem through the microphone.
7. See the speech converted into text.
8. Edit the transcript.
9. Submit it to the AI.
10. Receive the recommendation in the selected language.
11. Read the recommendation clearly.
12. Optionally listen to the recommendation.

The core experience must be reliable.

A smaller application that actually works is preferred over a huge application full of broken features.

---

# 36. FINAL DEMO FLOW

The recommended hackathon demonstration should be:

### Step 1

Open GreenTech.

### Step 2

Select:

Telugu / Hindi / Tamil / Kannada / English

### Step 3

Enter:

Rice / Paddy

### Step 4

Press microphone.

### Step 5

Speak naturally about the crop problem.

### Step 6

Show the generated transcript.

### Step 7

Edit the transcript if necessary.

### Step 8

Press:

Get Advice

### Step 9

Gemini analyzes:

- crop
- farmer's description
- agricultural knowledge
- selected language

### Step 10

Display:

Problem Summary
Possible Causes
What to Check
Recommended Actions
What to Avoid
Prevention
When to Contact an Agricultural Expert

### Step 11

Use:

Read Aloud

if the required voice is available.

This demonstrates the complete intended solution without unnecessary features.

---

# 37. JUDGE-FOCUSED VALUE

The project should demonstrate the following technical skills:

## Generative AI

Use Gemini for genuine natural-language agricultural reasoning.

## Multilingual AI

Allow farmers to communicate and receive recommendations in multiple Indian languages.

## Speech AI

Use Faster-Whisper for actual voice-to-text interaction.

## Agricultural Knowledge Layer

Combine local agricultural knowledge with generative AI.

## Recommendation Workflow

Convert a farmer's unstructured problem into practical recommendations.

## Software Engineering

Demonstrate:

- modular architecture
- dependency management
- environment configuration
- error handling
- API integration
- runtime testing

## Human-Centered Design

The farmer should NOT need to:

- know technical terminology
- use a predefined sentence
- understand AI prompts
- manually translate their problem

The interface should let the farmer simply describe the problem.

---

# 38. FINAL RULE

The priority order is:

1. WORKING CORE FUNCTIONALITY
2. VOICE
3. MULTILINGUAL SUPPORT
4. AGRICULTURAL AI REASONING
5. RELIABLE ERROR HANDLING
6. CLEAN UI
7. HISTORY/TTS
8. OPTIONAL FUTURE FEATURES

Do NOT sacrifice the working core for additional features.

Do NOT add image diagnosis, weather, farming calendar, complex reports, complicated databases, authentication, or other large features unless the core text + voice + multilingual advisory workflow is already stable.

The objective is:

SIMPLE.

RELIABLE.

MEANINGFUL.

ACTUALLY WORKING.

GreenTech should solve the stated problem rather than merely demonstrate a collection of technologies.