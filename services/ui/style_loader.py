import os
import base64
import streamlit as st
import streamlit.components.v1 as components


# ─────────────────────────────────────────────────────────────
# CORE LOADERS
# ─────────────────────────────────────────────────────────────

def load_css(file_path: str) -> None:
    """Inject a CSS file into the Streamlit app."""
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def inject_local_font(font_path: str, font_name: str) -> None:
    """
    Inject a local font file (OTF / TTF / WOFF2) as a base64 data URL.
    Call this before load_css so the font is ready when styles apply.
    """
    if not os.path.exists(font_path):
        return

    with open(font_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    ext = os.path.splitext(font_path)[1].lstrip(".").lower()
    fmt_map  = {"otf": "opentype", "ttf": "truetype", "woff": "woff", "woff2": "woff2"}
    mime_map = {"otf": "font/otf",  "ttf": "font/ttf",  "woff": "font/woff",  "woff2": "font/woff2"}
    fmt  = fmt_map.get(ext, ext)
    mime = mime_map.get(ext, f"font/{ext}")

    st.markdown(
        f"""
        <style>
        @font-face {{
            font-family: '{font_name}';
            src: url('data:{mime};base64,{encoded}') format('{fmt}');
            font-weight: 100 900;
            font-style: normal;
            font-display: swap;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_webrtc_styles(font_path: str | None = None) -> None:
    """
    Patch the WebRTC iframe with custom font + MUI button styles.
    Polls the parent document for iframes whose src contains 'webrtc'.
    Uses MutationObserver so it works even when the iframe loads lazily.
    """
    if font_path is None:
        font_path = os.path.join(os.getcwd(), "static", "AdobeClean.otf")

    encoded_font = ""
    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            encoded_font = base64.b64encode(f.read()).decode()

    font_face = (
        f"""
        @font-face {{
            font-family: 'AdobeClean';
            src: url('data:font/otf;base64,{encoded_font}') format('opentype');
            font-weight: 100 900;
            font-style: normal;
        }}
        """
        if encoded_font
        else ""
    )

    button_styles = """
        .MuiButtonBase-root,
        .MuiButton-root,
        .MuiButton-contained,
        .MuiButton-text {
            border-radius: 14px !important;
            font-family: 'AdobeClean', sans-serif !important;
            letter-spacing: 0.04em !important;
            text-transform: none !important;
            font-weight: 500 !important;
        }
        .MuiButton-contained {
            background: linear-gradient(135deg, #00C8FF, #0099CC) !important;
            color: #070A12 !important;
            box-shadow: 0 4px 16px rgba(0,200,255,0.25) !important;
        }
        .MuiButton-contained:hover {
            box-shadow: 0 6px 24px rgba(0,200,255,0.40) !important;
        }
    """

    components.html(
        f"""
        <script>
        (function patchWebRTCStyles() {{
            const STYLE_ID = 'webrtc-custom-styles';

            function injectIntoDoc(doc) {{
                if (!doc || !doc.head) return;
                if (doc.head.querySelector('#' + STYLE_ID)) return;
                const s = doc.createElement('style');
                s.id = STYLE_ID;
                s.textContent = `{font_face}{button_styles}`;
                doc.head.appendChild(s);
            }}

            function patchIframe(iframe) {{
                try {{
                    const cd = iframe.contentDocument;
                    if (cd && cd.readyState === 'complete') {{
                        injectIntoDoc(cd);
                    }} else {{
                        iframe.addEventListener('load', () => injectIntoDoc(iframe.contentDocument));
                    }}
                }} catch (e) {{
                    console.warn('[webrtc-patch] cross-origin block:', e);
                }}
            }}

            function findAndPatch() {{
                const parentDoc = window.parent.document;
                parentDoc.querySelectorAll('iframe').forEach(iframe => {{
                    if (iframe.src && iframe.src.includes('webrtc')) patchIframe(iframe);
                }});
            }}

            // Initial pass
            findAndPatch();

            // Watch for lazily-inserted iframes
            const observer = new MutationObserver(findAndPatch);
            observer.observe(window.parent.document.body, {{ childList: true, subtree: true }});
        }})();
        </script>
        """,
        height=0,
    )


# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────

def setup_page(
    title: str = "Kinetic",
    icon: str = "⚡",
    layout: str = "centered",
    font_path: str | None = None,
    css_path: str | None = None,
) -> None:
    """
    One-call setup: page config → font → CSS → webrtc patch.
    Call this at the top of every page / main script.
    """
    st.set_page_config(page_title=title, page_icon=icon, layout=layout)

    # Font
    _font_path = font_path or os.path.join(os.getcwd(), "static", "AdobeClean.otf")
    inject_local_font(_font_path, "AdobeClean")

    # CSS
    _css_path = css_path or os.path.join(os.getcwd(), "static", "style.css")
    load_css(_css_path)

    # WebRTC patch
    inject_webrtc_styles(_font_path)


# ─────────────────────────────────────────────────────────────
# REUSABLE UI COMPONENTS
# ─────────────────────────────────────────────────────────────

def render_page_header(title: str, subtitle: str = "", badge: str = "") -> None:
    """
    Premium page header with optional subtitle and badge pill.

    Usage:
        render_page_header("Workout Tracker", "Real-time pose analysis", badge="LIVE")
    """
    badge_html = (
        f'<span class="section-label">'
        f'<span class="live-dot"></span>{badge}'
        f'</span><br/>'
        if badge else ""
    )
    st.markdown(
        f"""
        <div style="margin-bottom: 2rem;">
            {badge_html}
            <h1 style="margin:0 0 0.3rem 0; font-size:2.1rem; font-weight:700;
                        background: linear-gradient(135deg, #F0F4FF 55%, #00C8FF 110%);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                        background-clip: text; letter-spacing:-0.03em; line-height:1.15;">
                {title}
            </h1>
            {"" if not subtitle else f'<p style="color:#8B96B0; font-size:0.9375rem; margin:0;">{subtitle}</p>'}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_label(text: str) -> None:
    """Tiny uppercase pill label to visually separate sections."""
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)


def render_stat_row(stats: list[dict]) -> None:
    """
    Render a horizontal row of stat badges.

    stats = [{"label": "Sets", "value": "4"}, ...]
    """
    badges = "".join(
        f'<span class="stat-badge"><strong>{s["value"]}</strong>&nbsp;{s["label"]}</span>'
        for s in stats
    )
    st.markdown(
        f'<div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:1rem;">'
        f'{badges}</div>',
        unsafe_allow_html=True,
    )


def render_labeled_divider(label: str = "") -> None:
    """Horizontal rule with optional centered label."""
    st.markdown(
        f'<div class="labeled-divider">{label}</div>',
        unsafe_allow_html=True,
    )


def render_glass_card(content_fn, *, padding: str = "1.5rem") -> None:
    """
    Wrap any Streamlit content in a glassmorphism card.

    Usage:
        def my_content():
            st.metric("Reps", 12)
            st.write("Keep it up!")

        render_glass_card(my_content)
    """
    st.markdown(
        f"""
        <div style="
            background: rgba(17, 24, 39, 0.70);
            backdrop-filter: blur(16px) saturate(160%);
            -webkit-backdrop-filter: blur(16px) saturate(160%);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 20px;
            padding: {padding};
            box-shadow: 0 4px 16px rgba(0,0,0,0.50);
            margin-bottom: 1rem;
            position: relative;
            overflow: hidden;
        ">
        <div style="
            position:absolute; top:0; left:0; right:0; height:1px;
            background: linear-gradient(90deg, transparent, rgba(0,200,255,0.20), transparent);
        "></div>
        """,
        unsafe_allow_html=True,
    )
    content_fn()
    st.markdown("</div>", unsafe_allow_html=True)


def render_webcam_wrapper(webcam_fn) -> None:
    """
    Wrap the WebRTC / camera component in a styled container
    with a live indicator and subtle glow.

    Usage:
        render_webcam_wrapper(lambda: webrtc_streamer(...))
    """
    st.markdown(
        """
        <div class="section-label" style="margin-bottom:0.75rem;">
            <span class="live-dot"></span>LIVE FEED
        </div>
        <div style="
            border-radius: 20px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 12px 40px rgba(0,0,0,0.60), 0 0 32px rgba(0,200,255,0.08);
            background: #111827;
            position: relative;
        ">
        """,
        unsafe_allow_html=True,
    )
    webcam_fn()
    st.markdown("</div>", unsafe_allow_html=True)


def render_metric_row(metrics: list[dict]) -> None:
    """
    Render metrics in a responsive column row.

    metrics = [
        {"label": "Calories", "value": "320", "delta": "+12"},
        {"label": "Heart Rate", "value": "142 bpm"},
    ]
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            st.metric(
                label=m.get("label", ""),
                value=m.get("value", "—"),
                delta=m.get("delta"),
            )


def render_info_banner(message: str, kind: str = "info") -> None:
    """
    Styled info / success / warning / error banner.
    kind ∈ {"info", "success", "warning", "error"}
    """
    color_map = {
        "info":    ("#00C8FF", "rgba(0,200,255,0.07)"),
        "success": ("#10B981", "rgba(16,185,129,0.08)"),
        "warning": ("#F59E0B", "rgba(245,158,11,0.08)"),
        "error":   ("#EF4444", "rgba(239,68,68,0.08)"),
    }
    icon_map = {"info": "ℹ️", "success": "✓", "warning": "⚠", "error": "✕"}
    color, bg = color_map.get(kind, color_map["info"])
    icon = icon_map.get(kind, "ℹ️")

    st.markdown(
        f"""
        <div style="
            background: {bg};
            border-left: 3px solid {color};
            border-radius: 0 12px 12px 0;
            padding: 0.75rem 1rem;
            display: flex;
            align-items: flex-start;
            gap: 0.6rem;
            margin-bottom: 1rem;
        ">
            <span style="color:{color}; font-size:0.9rem; flex-shrink:0;">{icon}</span>
            <p style="margin:0; color: #8B96B0; font-size:0.875rem; line-height:1.55;">{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_rep_counter(count: int, label: str = "REPS", accent: str = "#00C8FF") -> None:
    """
    Large, bold rep/set counter display for real-time trainer UI.
    """
    st.markdown(
        f"""
        <div style="
            text-align: center;
            padding: 2rem 1rem;
            background: rgba(17,24,39,0.70);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 24px;
            box-shadow: 0 0 32px rgba(0,200,255,0.06);
            margin-bottom: 1rem;
        ">
            <div style="
                font-size: 5rem;
                font-weight: 700;
                letter-spacing: -0.04em;
                line-height: 1;
                color: {accent};
                text-shadow: 0 0 40px {accent}55;
            ">{count}</div>
            <div style="
                font-size: 0.7rem;
                font-weight: 600;
                letter-spacing: 0.14em;
                text-transform: uppercase;
                color: #4A5568;
                margin-top: 0.5rem;
            ">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_logo(name: str = "KINETIC", tagline: str = "AI Gym Trainer") -> None:
    """Sidebar branding block."""
    st.sidebar.markdown(
        f"""
        <div style="
            padding: 0.25rem 0 1.5rem;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            margin-bottom: 1.5rem;
        ">
            <div style="
                font-size: 1.1rem;
                font-weight: 700;
                letter-spacing: 0.12em;
                background: linear-gradient(135deg, #F0F4FF, #00C8FF);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            ">{name}</div>
            <div style="
                font-size: 0.7rem;
                font-weight: 500;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: #4A5568;
                margin-top: 2px;
            ">{tagline}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_section(label: str) -> None:
    """Sidebar section label."""
    st.sidebar.markdown(
        f"""
        <div style="
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #4A5568;
            margin: 1.5rem 0 0.5rem;
            padding-left: 2px;
        ">{label}</div>
        """,
        unsafe_allow_html=True,
    )