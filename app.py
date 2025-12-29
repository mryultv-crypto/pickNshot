import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1] 픽앤샷 시그니처: 하이엔드 다크 UI ---
st.set_page_config(page_title="Pick & Shot: Anti-Gravity", page_icon="📸", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    div.stButton > button {
        width: 100%; height: 60px; font-weight: 800; font-size: 20px;
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%); 
        color: white; border: none; border-radius: 10px;
        box-shadow: 0 4px 15px rgba(37, 117, 252, 0.3);
    }
    .report-box { 
        background-color: #1E1E1E; padding: 30px; border-radius: 15px; 
        border: 1px solid #333; margin-bottom: 25px; color: #eee; line-height: 1.8;
    }
    h2, h3 { color: #f1f1f1 !important; border-bottom: 1px solid #444; padding-bottom: 10px; }
    b, strong { color: #ff9966; }
</style>
""", unsafe_allow_html=True)

# --- [2] 팩트 기반 엔진: 동적 모델 할당 (404 완벽 차단) ---
def get_verified_engine():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 최신 모델 우선 순위 (개발자님의 피드백 반영)
        for m in all_models:
            if any(v in m for v in ['2.5', '2.0', '1.5']) and 'flash' in m: return m
        return all_models[0] if all_models else None
    except: return None

# --- [3] 픽앤샷의 본질: 하이앤드 기획서 엔진 ---
def generate_high_end_strategy(image, engine):
    model = genai.GenerativeModel(engine)
    
    # 픽앤샷만의 고밀도 기획 프롬프트 (3가지 컨셉 프롬프트 포함)
    master_prompt = """
    You are a BCG Senior Strategist and a Creative Director for a World-Class Luxury Brand (like Hermès or Chanel).
    Analyze the uploaded product and create a "7-Star Master Marketing & Shooting Strategy".
    
    [CORE STRUCTURE - KOREAN]
    1. **Strategic Brand Positioning:** Define the core luxury value and psychological triggers.
    2. **Detailed Shooting Plan:** - Lighting: Define specific setups (e.g., Chiaroscuro, Butterfly lighting).
       - Props & Background: Suggest high-end materials (e.g., Carrara marble, raw silk).
       - Camera Angles: Specific lens and angle recommendations.

    [THREE CONCEPT IMAGE PROMPTS - ENGLISH (STRICTLY)]
    Provide 3 distinct, high-quality, photorealistic prompts for AI generation (DALL-E 3/Midjourney):
    
    Concept A: [Luxury Minimalist] - Focus on silent luxury and extreme detail.
    Concept B: [Cinematic Noir] - Focus on dramatic lighting and storytelling.
    Concept C: [Natural Avant-Garde] - Focus on artistic composition and organic elements.
    
    *Each prompt must include: 8k resolution, cinematic lighting, 85mm lens, f/1.8, photorealistic textures.*
    """
    
    try:
        response = model.generate_content([master_prompt, image])
        return response.text
    except Exception as e:
        return f"전략 생성 실패: {str(e)}"

# --- [4] 메인 UI ---
def main():
    with st.sidebar:
        st.title("🎛️ Control Tower")
        engine = get_verified_engine()
        if engine: st.success(f"Connected: {engine.replace('models/','')}")
        else: st.error("API 연결 실패")

    st.title("Pick & Shot 📸 : Master Edition")
    st.markdown("#### Anti-Gravity High-End Product Planning Studio")

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("1. 소재 업로드")
        file = st.file_uploader("High-Res Product Image", type=['jpg', 'png', 'jpeg'])
        shot_btn = st.button("🚀 마스터 기획안 생성")

    with col2:
        st.subheader("2. 미리보기")
        if file:
            img = Image.open(file)
            st.image(img, use_column_width=True)

    if shot_btn and file and engine:
        with st.status("🧠 BCG 전략팀이 7성급 기획안을 도출 중입니다...", expanded=True):
            result = generate_high_end_strategy(img, engine)
            
            st.divider()
            st.markdown(f'<div class="report-box">{result}</div>', unsafe_allow_html=True)
            
            # 컨셉별 프롬프트 섹션 강조
            if "Concept A" in result:
                st.subheader("🎨 3 Concepts High-End Prompts")
                st.info("AI 이미지 생성 엔진에 아래 프롬프트를 각각 입력하여 최고급 비주얼을 확인하세요.")

if __name__ == "__main__":
    main()
