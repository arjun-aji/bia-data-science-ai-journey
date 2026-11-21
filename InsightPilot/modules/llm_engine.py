"""
InsightPilot - LLM Engine Module
Handles reliable local Ollama communication, dynamic model detection,
simple natural Malayalam generation, and strict hallucination prevention.
"""

from typing import Dict, Any, Tuple, Optional, List
import json
import requests
import pandas as pd
from modules.data_analysis import get_numeric_columns, get_categorical_columns

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:3b"


def check_ollama_status() -> Tuple[bool, List[str], Optional[str]]:
    """
    Checks if Ollama service is reachable and retrieves installed models.
    Returns: (is_online, installed_model_names, error_message)
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2.5)
        if response.status_code == 200:
            data = response.json()
            models = [m.get("name") for m in data.get("models", []) if m.get("name")]
            return True, models, None
        return False, [], f"Ollama returned HTTP status {response.status_code}."
    except requests.exceptions.ConnectionError:
        return False, [], "Ollama is not running. Please start it using 'ollama serve' in your terminal."
    except requests.exceptions.Timeout:
        return False, [], "Ollama connection timed out."
    except Exception as e:
        return False, [], f"Error contacting Ollama: {e}"


def is_malayalam_requested(language: str, question: str = "") -> bool:
    """Detects whether Malayalam response is requested either by settings or text script."""
    lang_lower = language.lower()
    if "malayalam" in lang_lower:
        return True
    if "auto" in lang_lower and any('\u0D00' <= char <= '\u0D7F' for char in question):
        return True
    return False


def build_system_prompt(language: str = "English", question: str = "") -> str:
    """
    Constructs the authoritative system prompt enforcing factual accuracy
    and clean language output (Simple Malayalam or English).
    """
    if is_malayalam_requested(language, question):
        return """
You are InsightPilot, an AI Data Analyst communicating in SIMPLE, NATURAL MALAYALAM (ലളിതമായ മലയാളം).

CRITICAL MALAYALAM GUIDELINES:
1. Write in simple, natural, conversational Malayalam that everyone in Kerala easily understands.
2. Use simple, everyday Malayalam words:
   - Use 'ആകെ' for Total
   - Use 'ശരാശരി' for Average
   - Use 'ഏറ്റവും കൂടുതൽ' for Highest / Maximum
   - Use 'ഏറ്റവും കുറഞ്ഞ' for Lowest / Minimum
   - Use 'വിൽപ്പന' for Sales
   - Use 'എണ്ണം' for Quantity
   - Use 'വരുമാനം' for Revenue
   - Use 'ഉൽപ്പന്നങ്ങൾ' for Products
3. Format your response into 3 or 4 clear bullet points (•).
4. Keep technical names in English (e.g. Laptop, Phone, Tablet, Sales).
5. Ensure proper space between words and numbers. Never glue words together.
6. Base all statements strictly on the verified facts provided. Do not invent any numbers.
""".strip()
    else:
        return """
You are InsightPilot, an AI data analyst.
Analyze only the supplied dataset context and computed results.
Do not invent values. Explain findings clearly and simply in professional English.
Format your answer with clear bullet points.
Treat Python calculations as strictly authoritative.
""".strip()


def query_ollama(
    model: str,
    user_prompt: str,
    system_prompt: Optional[str] = None,
    timeout: int = 180
) -> str:
    """
    Sends request to local Ollama chat API with error handling.
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False
            },
            timeout=timeout
        )
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Cannot connect to Ollama. Please ensure Ollama is running (`ollama serve`) "
            f"and reachable at {OLLAMA_BASE_URL}."
        )
    except requests.exceptions.Timeout:
        raise TimeoutError(
            f"The AI request timed out after {timeout} seconds. Ollama took too long to respond."
        )
    except Exception as e:
        raise RuntimeError(f"Ollama request error: {e}")

    if response.status_code == 404:
        raise RuntimeError(
            f"The model '{model}' was not found in Ollama. "
            f"Please download it by running: `ollama pull {model}` in your terminal."
        )

    if not response.ok:
        try:
            err_msg = response.json().get("error", response.text)
        except Exception:
            err_msg = response.text
        raise RuntimeError(f"Ollama error ({response.status_code}): {err_msg}")

    result = response.json()
    content = result.get("message", {}).get("content", "").strip()
    if not content:
        raise RuntimeError("Ollama returned an empty response.")
    return content


def explain_findings(
    df: pd.DataFrame,
    question: str,
    verified_context: Optional[Dict[str, Any]] = None,
    model: str = DEFAULT_MODEL,
    language: str = "English"
) -> str:
    """
    Orchestrates grounded AI explanation for questions, using either verified Python findings
    or concise dataset context. Enforces clean Simple Malayalam when requested.
    """
    system_prompt = build_system_prompt(language=language, question=question)
    use_ml = is_malayalam_requested(language, question)

    if verified_context:
        if use_ml:
            prompt = f"""
ചോദ്യം: "{question}"

കണ്ടെത്തിയ പ്രധാന വിവരങ്ങൾ (Authoritative Facts):
{json.dumps(verified_context, indent=2, default=str)}

നിർദ്ദേശങ്ങൾ:
1. മുകളിൽ നൽകിയിരിക്കുന്ന വിവരങ്ങൾ മാത്രം അടിസ്ഥാനമാക്കി ലളിതമായ മലയാളത്തിൽ (Simple Malayalam) 2-3 വരികളിൽ വിശദീകരിക്കുക.
2. പ്രധാന ഉൽപ്പന്നം, തുക എന്നിവ വ്യക്തമായി പറയുക.
3. കഠിനമായ വാക്കുകൾ ഒഴിവാക്കി ലളിതമായ ശൈലി ഉപയോഗിക്കുക.
"""
        else:
            prompt = f"""
USER QUESTION:
"{question}"

VERIFIED PYTHON COMPUTED FINDINGS:
{json.dumps(verified_context, indent=2, default=str)}

INSTRUCTIONS:
1. Explain this verified finding in clear, simple English.
2. Highlight the key business takeaway in 2-3 concise bullet points.
3. Treat all numbers in the verified findings as strictly authoritative.
"""
    else:
        # Build clean formatted context
        columns = list(df.columns)
        num_cols = get_numeric_columns(df)
        cat_cols = get_categorical_columns(df)

        stats_lines = []
        for col in num_cols:
            stats_lines.append(
                f"- {col}: Total = {df[col].sum():,.2f}, Average = {df[col].mean():,.2f}, "
                f"Median = {df[col].median():,.2f}, Min = {df[col].min():,.2f}, Max = {df[col].max():,.2f}"
            )
        stats_summary = "\n".join(stats_lines) if stats_lines else "No numeric columns."

        cat_summary = {}
        for col in cat_cols[:3]:
            cat_summary[col] = df[col].value_counts().head(5).to_dict()

        if use_ml:
            prompt = f"""
ഡാറ്റാസെറ്റ് വിവരങ്ങൾ:
• കോളങ്ങൾ: {', '.join(columns)}
• ആകെ വരികൾ: {len(df)}
• പ്രധാന സംഖ്യാ വിവരങ്ങൾ:
{stats_summary}
• വിഭാഗങ്ങൾ (Categories):
{json.dumps(cat_summary, default=str)}

ഉപയോക്താവിന്റെ ചോദ്യം:
"{question}"

പ്രധാന നിർദ്ദേശങ്ങൾ:
1. ഈ ഡാറ്റാസെറ്റിനെക്കുറിച്ച് ലളിതമായ മലയാളത്തിൽ (Simple, Natural Malayalam) 3 അല്ലെങ്കിൽ 4 ബുള്ളറ്റ് പോയിന്റുകളിൽ (•) വിശദീകരിക്കുക.
2. ഉദാഹരണം:
   • ഈ ഡാറ്റയിൽ ആകെ {len(df)} വിൽപ്പന വിവരങ്ങൾ ഉണ്ട്.
   • ഏറ്റവും കൂടുതൽ വിൽപ്പനയുള്ളത് ഏത് ഉൽപ്പന്നത്തിനാണ് എന്ന് വ്യക്തമാക്കുക.
   • ശരാശരി വിൽപ്പന തുക എത്രയാണെന്ന് പറയുക.
3. അനാവശ്യമായ ഇംഗ്ലീഷ് വാക്കുകൾ മലയാളത്തിൽ എഴുതാതെ, ലളിതമായ വാക്കുകൾ ഉപയോഗിക്കുക (ഉദാഹരണത്തിന്: 'ആകെ', 'ശരാശരി', 'കൂടുതൽ').
4. പുതിയ സംഖ്യകൾ ഉണ്ടാക്കരുത്.
"""
        else:
            prompt = f"""
DATASET SCHEMA & SUMMARY:
• Columns: {', '.join(columns)}
• Total Records: {len(df)}
• Numeric Statistics:
{stats_summary}
• Key Categories:
{json.dumps(cat_summary, default=str)}

USER QUESTION:
"{question}"

INSTRUCTIONS:
1. Answer the question using only the dataset information provided above.
2. Structure your response in 3-4 clean, insightful bullet points.
3. Do not invent numbers.
"""

    return query_ollama(model=model, user_prompt=prompt, system_prompt=system_prompt)


# ==========================================
# VOICE & MULTIMODAL ARCHITECTURE HOOK
# ==========================================
class VoiceAssistantHook:
    """
    Architectural extension point for macOS Apple Silicon speech integration.
    Allows future plug-in of local speech recognition (e.g. Whisper.cpp)
    or browser-native HTML5 Web Speech API for Malayalam & English.
    """
    @staticmethod
    def is_voice_available() -> bool:
        return True

    @staticmethod
    def get_supported_locales() -> List[str]:
        return ["en-US", "ml-IN"]

