# ui_components.py

def get_header_html() -> str:
    bars = "".join(["<span></span>"] * 10)
    return f"""
    <div class="voxis-header">
      <div class="voxis-eyebrow">Azure Cognitive Services · AI Voice Studio</div>
      <div class="voxis-wordmark">VOXIS</div>
      <div class="voxis-tagline">Transform Voice · Transcribe Speech · Synthesise Sound · Extract Text</div>
      <div class="voxis-divider"></div>
      <div class="waveform-deco">{bars}</div>
    </div>
    """

def get_panel_html(num: str, title: str, desc: str) -> str:
    return f"""
    <div class="panel">
      <div class="panel-label">{num} &nbsp; {title.split(' ')[0]}</div>
      <div class="panel-title">{title}</div>
      <div class="panel-desc">{desc}</div>
    </div>
    """

def get_info_box_html(label: str, content: str) -> str:
    return f"""
    <div style="background:var(--surface-2);border:1px solid var(--border-soft);
                border-radius:var(--radius-md);padding:1rem 1.2rem;margin-top:0.8rem;">
      <div style="font-family:var(--font-mono);font-size:0.6rem;
                  letter-spacing:0.25em;color:var(--gold);text-transform:uppercase;">
        {label}
      </div>
      <div style="font-size:0.78rem;color:var(--cream-dim);margin-top:0.6rem;line-height:1.8;">
        {content}
      </div>
    </div>
    """

def get_result_html(text: str, label: str) -> str:
    word_count = len(text.split())
    char_count = len(text)
    return f"""
    <div class="result-box">
      <div class="result-label">✦ {label}</div>
      <div class="result-text">{text}</div>
      <div class="stat-row">
        <div class="stat-chip"><b>{word_count}</b> words</div>
        <div class="stat-chip"><b>{char_count}</b> characters</div>
      </div>
    </div>
    """

def get_confidence_box_html(confidence: float) -> str:
    return f"""
    <div style="margin-top:1rem;padding:0.8rem;background:var(--surface-3);
                border:1px solid var(--border-soft);border-radius:var(--radius-md);">
      <div style="font-family:var(--font-mono);font-size:0.62rem;
                  letter-spacing:0.15em;color:var(--gold);text-transform:uppercase;">
        Recognition Confidence
      </div>
      <div style="font-size:1.1rem;color:var(--white);font-weight:600;margin-top:0.4rem;">
        {confidence:.1%}
      </div>
    </div>
    """

def get_footer_html() -> str:
    return """
    <div class="voxis-footer">
      VOXIS · Powered by Azure Cognitive Services · Built with Streamlit<br>
      Made by Ankit Tank
    </div>
    """