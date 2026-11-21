"""
InsightPilot - Voice Command Engine
Provides interactive in-browser speech recognition (HTML5 Web Speech API)
supporting English and Malayalam (ml-IN), with automatic query execution
and direct Streamlit input synchronization.
"""

import streamlit as st
import streamlit.components.v1 as components


def render_voice_input_widget(language: str = "English") -> None:
    """
    Renders an interactive, stylish speech-to-text widget.
    Allows user to speak in English or Malayalam and AUTOMATICALLY triggers
    analysis by copying spoken text directly into the Streamlit question box
    and clicking the Analyze button.
    """
    is_ml = "malayalam" in language.lower()
    default_lang_code = "ml-IN" if is_ml else "en-US"

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * {{
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                margin: 0;
                padding: 4px;
                background: transparent;
                color: #f8fafc;
            }}
            .voice-card {{
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.98) 100%);
                border: 1px solid rgba(56, 189, 248, 0.35);
                border-radius: 12px;
                padding: 14px 18px;
                display: flex;
                flex-direction: column;
                gap: 10px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
            }}
            .voice-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 8px;
            }}
            .voice-title {{
                font-size: 14px;
                font-weight: 700;
                color: #38bdf8;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .lang-badge {{
                background: rgba(56, 189, 248, 0.15);
                color: #38bdf8;
                border: 1px solid rgba(56, 189, 248, 0.4);
                padding: 3px 12px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            .lang-badge:hover {{
                background: rgba(56, 189, 248, 0.3);
            }}
            .controls-row {{
                display: flex;
                align-items: center;
                gap: 12px;
                flex-wrap: wrap;
            }}
            .mic-btn {{
                background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
                color: white;
                border: none;
                padding: 9px 16px;
                border-radius: 8px;
                font-weight: 700;
                font-size: 13px;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                transition: all 0.2s ease;
                box-shadow: 0 2px 10px rgba(2, 132, 199, 0.4);
            }}
            .mic-btn:hover {{
                transform: translateY(-1px);
                box-shadow: 0 4px 15px rgba(2, 132, 199, 0.6);
            }}
            .mic-btn.listening {{
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                animation: pulse 1.4s infinite;
            }}
            @keyframes pulse {{
                0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }}
                70% {{ box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }}
            }}
            .status-text {{
                font-size: 12px;
                color: #94a3b8;
                flex: 1;
                min-width: 200px;
            }}
            .transcript-box {{
                background: rgba(15, 23, 42, 0.7);
                border: 1px dashed rgba(56, 189, 248, 0.35);
                border-radius: 8px;
                padding: 9px 14px;
                font-size: 13px;
                color: #f1f5f9;
                min-height: 24px;
                line-height: 1.4;
            }}
            .auto-btn {{
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 700;
                cursor: pointer;
                display: none;
                align-self: flex-start;
                box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
                transition: all 0.2s ease;
            }}
            .auto-btn:hover {{
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.5);
            }}
        </style>
    </head>
    <body>
        <div class="voice-card">
            <div class="voice-header">
                <div class="voice-title">
                    <span>🎙️ Voice Command Assistant (Auto-Execute)</span>
                </div>
                <div class="lang-badge" id="langDisplay" onclick="toggleLanguage()" title="Click to toggle language">
                    {"Malayalam (മലയാളം)" if default_lang_code == "ml-IN" else "English (en-US)"}
                </div>
            </div>

            <div class="controls-row">
                <button class="mic-btn" id="micButton" onclick="toggleRecognition()">
                    <span id="micIcon">🎙️</span>
                    <span id="btnLabel">{"സംസാരിക്കുക (Speak Now)" if default_lang_code == "ml-IN" else "Speak Now"}</span>
                </button>
                <span class="status-text" id="statusMessage">Click mic, speak your question — it copies &amp; analyzes automatically!</span>
            </div>

            <div class="transcript-box" id="transcriptDisplay">
                {"മൈക്കിൽ ക്ലിക്ക് ചെയ്ത് ചോദ്യം ചോദിക്കുക..." if default_lang_code == "ml-IN" else "Click mic and speak your question..."}
            </div>

            <button class="auto-btn" id="analyzeNowBtn" onclick="submitNow()">
                🚀 {"ഇപ്പോൾ വിശകലനം ചെയ്യുക (Analyze Now)" if default_lang_code == "ml-IN" else "Analyze Spoken Question Now"}
            </button>
        </div>

        <script>
            let recognition = null;
            let isListening = false;
            let finalRecordedText = "";
            let currentLang = "{default_lang_code}";

            function initRecognition() {{
                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    recognition = new SpeechRecognition();
                    recognition.continuous = false;
                    recognition.interimResults = true;
                    recognition.lang = currentLang;

                    recognition.onstart = function() {{
                        isListening = true;
                        finalRecordedText = "";
                        document.getElementById('micButton').classList.add('listening');
                        document.getElementById('btnLabel').innerText = currentLang === 'ml-IN' ? "കേൾക്കുന്നു... (Listening)" : "Listening...";
                        document.getElementById('statusMessage').innerText = currentLang === 'ml-IN' ? "മൈക്കിൽ ചോദ്യം പറയൂ..." : "Speak now into your microphone...";
                        document.getElementById('transcriptDisplay').innerText = "...";
                        document.getElementById('analyzeNowBtn').style.display = 'none';
                    }};

                    recognition.onresult = function(event) {{
                        let interim = '';
                        let final = '';
                        for (let i = event.resultIndex; i < event.results.length; ++i) {{
                            if (event.results[i].isFinal) {{
                                final += event.results[i][0].transcript;
                            }} else {{
                                interim += event.results[i][0].transcript;
                            }}
                        }}
                        const currentText = (final || interim).trim();
                        if (currentText) {{
                            finalRecordedText = currentText;
                            document.getElementById('transcriptDisplay').innerText = '"' + currentText + '"';
                            document.getElementById('analyzeNowBtn').style.display = 'inline-block';
                        }}
                    }};

                    recognition.onerror = function(event) {{
                        isListening = false;
                        document.getElementById('micButton').classList.remove('listening');
                        document.getElementById('btnLabel').innerText = "Try Again";
                        document.getElementById('statusMessage').innerText = "Mic notice: " + (event.error || "error occurred");
                    }};

                    recognition.onend = function() {{
                        isListening = false;
                        document.getElementById('micButton').classList.remove('listening');
                        document.getElementById('btnLabel').innerText = currentLang === 'ml-IN' ? "വീണ്ടും പറയുക (Speak Again)" : "Speak Again";

                        if (finalRecordedText && finalRecordedText.trim().length > 1) {{
                            document.getElementById('statusMessage').innerHTML = "<span style='color:#38bdf8;font-weight:700;'>🚀 Speech captured! Copying to question box &amp; analyzing...</span>";
                            setTimeout(() => {{
                                submitNow();
                            }}, 300);
                        }} else {{
                            document.getElementById('statusMessage').innerText = "No speech detected. Click mic to try again.";
                        }}
                    }};
                }} else {{
                    document.getElementById('statusMessage').innerText = "Browser Web Speech API not supported. Please use Google Chrome.";
                    document.getElementById('micButton').disabled = true;
                }}
            }}

            initRecognition();

            function toggleLanguage() {{
                if (isListening && recognition) {{
                    recognition.stop();
                }}
                if (currentLang === 'en-US') {{
                    currentLang = 'ml-IN';
                    document.getElementById('langDisplay').innerText = "Malayalam (മലയാളം)";
                    document.getElementById('btnLabel').innerText = "സംസാരിക്കുക (Speak Now)";
                }} else {{
                    currentLang = 'en-US';
                    document.getElementById('langDisplay').innerText = "English (en-US)";
                    document.getElementById('btnLabel').innerText = "Speak Now";
                }}
                initRecognition();
            }}

            function toggleRecognition() {{
                if (!recognition) return;
                if (isListening) {{
                    recognition.stop();
                }} else {{
                    try {{
                        recognition.start();
                    }} catch (e) {{
                        recognition.stop();
                        setTimeout(() => recognition.start(), 200);
                    }}
                }}
            }}

            // Updates React-controlled input element correctly
            function setNativeInputValue(element, value) {{
                if (!element) return;
                try {{
                    element.focus();
                    const win = element.ownerDocument ? element.ownerDocument.defaultView : window;
                    const prototype = win.HTMLInputElement ? win.HTMLInputElement.prototype : Object.getPrototypeOf(element);
                    const descriptor = Object.getOwnPropertyDescriptor(prototype, 'value');
                    if (descriptor && descriptor.set) {{
                        descriptor.set.call(element, value);
                    }} else {{
                        element.value = value;
                    }}
                    element.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                    element.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
                }} catch (e) {{
                    console.error("Native input setter failed:", e);
                    element.value = value;
                }}
            }}

            function getParentDocument() {{
                try {{
                    if (window.parent && window.parent.document) {{
                        return window.parent.document;
                    }}
                }} catch (e) {{
                    console.warn("Cross-frame parent document restricted:", e);
                }}
                return null;
            }}

            function findQuestionInput(doc) {{
                if (!doc) return null;
                // Try finding by aria-label
                let el = doc.querySelector('input[aria-label="Your Analysis Question:"]');
                if (el) return el;

                // Try finding by placeholder
                const inputs = Array.from(doc.querySelectorAll('input[type="text"], input[data-testid="stTextInput"]'));
                for (const inp of inputs) {{
                    const ph = (inp.getAttribute('placeholder') || '').toLowerCase();
                    if (ph.includes('ask any question') || ph.includes('ചോദ്യം') || ph.includes('sales')) {{
                        return inp;
                    }}
                }}

                // Fallback to any input in Streamlit input container
                const stInputs = doc.querySelectorAll('.stTextInput input');
                if (stInputs.length > 0) {{
                    return stInputs[stInputs.length - 1];
                }}
                return null;
            }}

            function findAnalyzeButton(doc) {{
                if (!doc) return null;
                const buttons = Array.from(doc.querySelectorAll('button'));
                for (const btn of buttons) {{
                    const txt = (btn.innerText || btn.textContent || '').trim();
                    if ((txt.includes('Analyze') || txt.includes('വിശകലനം')) && !btn.closest('.stTabs')) {{
                        return btn;
                    }}
                }}
                return null;
            }}

            function submitNow() {{
                const textToSend = finalRecordedText.trim();
                if (!textToSend || textToSend === "..." || textToSend.length < 2) {{
                    document.getElementById('statusMessage').innerText = "Please speak a question first.";
                    return;
                }}

                const statusEl = document.getElementById('statusMessage');
                const actionBtn = document.getElementById('analyzeNowBtn');
                statusEl.innerHTML = "<span style='color: #38bdf8;'>⏳ Copying to input box &amp; analyzing...</span>";
                actionBtn.innerText = "⏳ Analyzing...";

                let injected = false;
                const parentDoc = getParentDocument();

                if (parentDoc) {{
                    const inputElem = findQuestionInput(parentDoc);
                    if (inputElem) {{
                        setNativeInputValue(inputElem, textToSend);
                        injected = true;

                        // Give React time to register state, then click Analyze
                        setTimeout(() => {{
                            const btn = findAnalyzeButton(parentDoc);
                            if (btn) {{
                                btn.click();
                                statusEl.innerHTML = "<span style='color: #10b981; font-weight: 700;'>✅ Question copied &amp; analyzed successfully!</span>";
                                actionBtn.innerText = "✅ Analyzed!";
                            }} else {{
                                inputElem.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }}));
                                statusEl.innerHTML = "<span style='color: #10b981; font-weight: 700;'>✅ Question copied &amp; submitted!</span>";
                                actionBtn.innerText = "✅ Submitted!";
                            }}
                        }}, 150);
                    }}
                }}

                // Clipboard backup
                if (navigator.clipboard && navigator.clipboard.writeText) {{
                    navigator.clipboard.writeText(textToSend).catch(() => {{}});
                }}

                if (!injected) {{
                    statusEl.innerHTML = "<span style='color: #38bdf8;'>📋 Copied to clipboard! Paste into question box and click Analyze.</span>";
                    actionBtn.innerText = "📋 Copied!";
                }}
            }}
        </script>
    </body>
    </html>
    """

    components.html(html_code, height=210)
