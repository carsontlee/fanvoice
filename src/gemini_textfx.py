import os
import google.generativeai as genai

# Configure the Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables or .env file.")

genai.configure(api_key=GEMINI_API_KEY)

TEXTFX_MODELS = {
    "Simile": {
        "name": "Simile (Create a simile about a thing or concept.)",
        "prompt_components": {
            "preamble": "This tool takes a thing or concept and returns a single, creative simile about it, as one complete sentence.",
            "prefixes": ["Thing/Concept", "Simile"],
            "examples": [
                ["A beautiful sunset", "A beautiful sunset is like a painting in the sky, its colors bleeding into the canvas of the evening."],
                ["A very tall building", "The skyscraper pierced the clouds like a needle threaded with the ambition of the city."],
                ["illusion", "The promise hung in the air like a half-remembered melody, beautiful but ultimately fading into silence."]
            ],
        },
        "temperature": 0.8,
        "max_tokens": 150,
        "output_type": "single_sentence"
    },
    "Explode": {
        "name": "Explode (Break a word into similar-sounding phrases.)",
        "prompt_components": {
            "preamble": "This tool takes a word and breaks it into similar-sounding phrases, often with a parenthetical explanation. Provide just the exploded phrase and its explanation.",
            "prefixes": ["Word", "Exploded Phrase"],
            "examples": [
                ["hello", "hell low (a greeting from a low place)"],
                ["computer", "comp uter (a friend who tells you to come to the computer)"],
                ["illusion", "ill u shun (to ignore someone who is ill)"]
            ],
        },
        "temperature": 0.7,
        "max_tokens": 100,
        "output_type": "single_sentence"
    },
    "Unexpect": {
        "name": "Unexpect (Make a scene more unexpected and imaginative.)",
        "prompt_components": {
            "preamble": "This tool takes a brief scene description and makes it more unexpected and imaginative in a single, concise sentence, preserving the core of the original scene but adding a surprising twist.",
            "prefixes": ["Scene", "Unexpected Scene"],
            "examples": [
                ["A child playing in a sandbox.", "A child played in a sandbox where the grains of sand whispered ancient secrets."],
                ["A cat drinking from a bowl of milk.", "The cat lapped at the bowl of milk, which glowed faintly with starlight."],
                ["illusion", "An illusion so realistic, it fooled the illusionist himself."]
            ],
        },
        "temperature": 0.9,
        "max_tokens": 150,
        "output_type": "single_sentence"
    },
    "Chain": {
        "name": "Chain (Build a chain of semantically related items.)",
        "prompt_components": {
            "preamble": "This tool takes a word and returns a chain of semantically related items as a comma-separated list. The items in the chain should be related to the previous item.",
            "prefixes": ["Word", "Chain"],
            "examples": [
                ["house", "house, home, dwelling, abode, residence, structure, building"],
                ["car", "car, automobile, vehicle, motorcar, machine, transport, engine"],
                ["illusion", "illusion, magic, rabbit, hat, head, mind, thought, reality"]
            ],
        },
        "temperature": 0.7,
        "max_tokens": 150,
        "output_type": "comma_list"
    },
    "Acronym": {
        "name": "Acronym (Create an acronym using the letters of a word.)",
        "prompt_components": {
            "preamble": "This tool takes a word and returns a creative or descriptive phrase that forms an acronym from its letters, in the format WORD - Phrase. Do not use asterisks or other special formatting around the letters.",
            "prefixes": ["Word", "Acronym"],
            "examples": [
                ["laser", "LASER - Light Amplification by Stimulated Emission of Radiation"],
                ["scuba", "SCUBA - Self-Contained Underwater Breathing Apparatus"],
                ["cat", "CAT - Creative Animal Talents"]
            ],
        },
        "temperature": 0.7,
        "max_tokens": 100,
        "output_type": "single_sentence"
    },
    "Scene": {
        "name": "Scene (Generate sensory details about a scene.)",
        "prompt_components": {
            "preamble": "This tool takes a concept or word and generates a short, evocative sentence describing a scene related to it. Do not start the sentence with \"Scene:\".",
            "prefixes": ["Concept/Word", "Scene Description"],
            "examples": [
                ["A forest after a rainstorm.", "Sunlight dappled the damp earth, carrying the scent of pine and wet leaves."],
                ["A crowded market in a foreign city.", "Spices hung heavy in the air, mingling with the calls of vendors and the bright colors of unfamiliar fruits."],
                ["illusion", "Shimmering, iridescent fabric draped over a hidden frame."]
            ],
        },
        "temperature": 0.8,
        "max_tokens": 150,
        "output_type": "single_sentence"
    },
    "Unfold": {
        "name": "Unfold (Slot a word into other words or phrases.)",
        "prompt_components": {
            "preamble": "This tool takes a word and returns a common phrase or compound term where the word is naturally used. Provide just the phrase or term.",
            "prefixes": ["Word", "Unfolded Phrase/Term"],
            "examples": [
                ["cat", "cat nap"],
                ["dog", "dog days"],
                ["sun", "sunflower"],
                ["illusion", "illusion of grandeur"]
            ],
        },
        "temperature": 0.7,
        "max_tokens": 100,
        "output_type": "single_sentence"
    }
}

def list_available_models():
    print("Available Gemini Models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model Name: {m.name}")
            print(f"  Description: {m.description}")
            print(f"  Supported Generation Methods: {m.supported_generation_methods}")
            print("---")

def generate_text_effect(effect_name_with_desc, input_text):
    effect_key = None
    for key, model_data in TEXTFX_MODELS.items():
        if effect_name_with_desc == model_data["name"]:
            effect_key = key
            break
    
    if not effect_key:
        return "Error: Selected TextFX tool not found by full name."

    model_config = TEXTFX_MODELS[effect_key]
    prompt_components = model_config["prompt_components"]
    
    full_prompt_lines = []
    if prompt_components.get("preamble"):
        full_prompt_lines.append(prompt_components["preamble"])
        full_prompt_lines.append("")

    if prompt_components.get("examples"):
        for example_values in prompt_components["examples"]:
            for i, ex_val in enumerate(example_values):
                prefix = prompt_components["prefixes"][i]
                full_prompt_lines.append(f"{prefix}: {ex_val}")
            full_prompt_lines.append("") 
    
    input_prefix = prompt_components["prefixes"][0]
    full_prompt_lines.append(f"{input_prefix}: {input_text}")
    
    output_prefix = prompt_components["prefixes"][-1]
    full_prompt_lines.append(f"{output_prefix}:")

    final_prompt = "\n".join(full_prompt_lines)

    try:
        # Updated model name to a generally available one
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest") 
        response = model.generate_content(
            final_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=model_config.get("temperature", 0.7),
                max_output_tokens=model_config.get("max_tokens", 100)
            )
        )
        raw_text = response.text.strip()
        
        if model_config.get("output_type") == "single_sentence":
            raw_text = raw_text.lstrip("-* ").replace("\n", " ").strip()
            return raw_text
        elif model_config.get("output_type") == "comma_list":
            raw_text = raw_text.replace("\n", ", ").replace("- ", "").replace("* ", "")
            raw_text = ", ".join(item.strip() for item in raw_text.split(",") if item.strip())
            return raw_text
        else: 
            return raw_text
            
    except Exception as e:
        print(f"Error generating text with Gemini: {e}")
        if "404" in str(e) and "model" in str(e).lower():
             return f"Error generating creative text: The specified generative model was not found or is not available. Please check the model name. Details: {str(e)}"
        return f"Error generating creative text: {str(e)}"

if __name__ == "__main__":
    # list_available_models() # Keep this commented out for now, or run separately if needed.
    print("\nAvailable tools (full names with descriptions):")
    for model_data in TEXTFX_MODELS.values():
        print(f"- {model_data['name']}")

    test_cases = [
        ("Simile (Create a simile about a thing or concept.)", "freedom"),
        ("Explode (Break a word into similar-sounding phrases.)", "together"),
        ("Unexpect (Make a scene more unexpected and imaginative.)", "a librarian reading a book"),
        ("Chain (Build a chain of semantically related items.)", "ocean"),
        ("Acronym (Create an acronym using the letters of a word.)", "dream"),
        ("Scene (Generate sensory details about a scene.)", "a forgotten attic"),
        ("Unfold (Slot a word into other words or phrases.)", "light")
    ]

    # Rerun test cases to check the new model
    for tool_name, input_val in test_cases:
        print(f"\n--- Testing Tool: {tool_name} ---")
        print(f"Input: {input_val}")
        result = generate_text_effect(tool_name, input_val)
        print(f"Output: {result}")

