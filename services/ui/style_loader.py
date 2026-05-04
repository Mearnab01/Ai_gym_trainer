import os
import base64
import streamlit as st
import streamlit.components.v1 as components


# ── helpers ───────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _encode_file(path: str) -> str:
    """Base64-encode a file once and cache it for the session."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ── public API ────────────────────────────────────────────────────────────────

def load_css(file_path: str) -> None:
    """Inject a local CSS file into the Streamlit app."""
    if not os.path.exists(file_path):
        return
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def inject_local_font(font_path: str, font_name: str) -> None:
    """Embed a local font file (ttf / otf / woff2) as a base64 @font-face."""
    if not os.path.exists(font_path):
        return

    ext = os.path.splitext(font_path)[1].lstrip(".").lower()
    fmt  = "opentype" if ext == "otf" else ext          
    mime = f"font/{ext}"

    st.markdown(f"""
        <style>
        @font-face {{
            font-family: '{font_name}';
            src: url('data:{mime};base64,{_encode_file(font_path)}') format('{fmt}');
            font-weight: 100 900;
            font-style: normal;
        }}
        </style>
    """, unsafe_allow_html=True)


def inject_webrtc_styles() -> None:
    """
    Patch MUI / WebRTC iframes with the local AdobeClean font.
    No-ops silently when the font file is missing.
    """
    font_path = os.path.join(os.getcwd(), "static", "AdobeClean.otf")
    if not os.path.exists(font_path):
        return

    encoded = _encode_file(font_path)

    components.html(f"""
        <script>
        (function () {{
            const STYLE_ID = 'webrtc-custom-styles';
            const FONT_SRC = 'data:font/otf;base64,{encoded}';

            function injectIntoIframe(iframe) {{
                try {{
                    const doc = iframe.contentDocument || iframe.contentWindow?.document;
                    if (!doc?.head || doc.head.querySelector('#' + STYLE_ID)) return;

                    const style = doc.createElement('style');
                    style.id = STYLE_ID;
                    style.textContent = `
                        @font-face {{
                            font-family: 'AdobeClean';
                            src: url('${{FONT_SRC}}') format('opentype');
                            font-weight: 100 900;
                        }}
                        .MuiButtonBase-root, .MuiButton-root {{
                            border-radius: 0 !important;
                            font-family: 'AdobeClean', sans-serif !important;
                            letter-spacing: 0.05em !important;
                        }}
                    `;
                    doc.head.appendChild(style);
                }} catch (e) {{
                    console.warn('[webrtc-patcher]', e);
                }}
            }}

            window.parent.document
                .querySelectorAll('iframe')
                .forEach(iframe => {{
                    if (!iframe.src?.includes('webrtc')) return;
                    iframe.contentDocument?.readyState === 'complete'
                        ? injectIntoIframe(iframe)
                        : iframe.addEventListener('load', () => injectIntoIframe(iframe));
                }});
        }})();
        </script>
    """, height=0)