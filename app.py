import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1] BCG & VOGUE 하이엔드 스타일링 ---
st.set_page_config(page_title="Pick & Shot: Enterprise", page_icon="📸", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    div.stButton > button {
        width: 100%; border-radius: 8px; height: 55px; font-weight: 800; font-size: 18px;
        background: linear-gradient(90deg, #FF4B4B 0%, #FF9966 100%); color: white; border: none;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3); transition: all 0.3s ease;
    }
    .report-box {
        background-color: #1E1E1E; padding: 25px; border-radius: 12px; 
        border: 1px solid #333; margin-bottom: 20px; color: #eee; line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# --- [2] SaaS 라이선스 시스템 ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "BASIC-1234": {"plan": "BASIC", "usage": 0, "limit": 30},
        "PRO-5678":   {"plan": "PRO",   "usage": 0, "limit": 100},
        "PREM-9999":  {"plan": "PREMIUM", "usage": 0, "limit": 300}
    }

# --- [3] 핵심 엔진: 모델 자동 매칭 (404 원천 차단) ---
def get_available_engine():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        # 내 API 키가 허용하는 모델 리스트를 서버에서 직접 긁어옴
        models = [m.name.replace('models/', '') for m in genai.list_models() 
                  if 'generateContent' in m.supported_generation_methods]
        
        # 선호 순위: 1.5-flash -> 1.5-pro -> pro-vision -> pro
        for target in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro-vision', 'gemini-pro']:
            if target in models: return target
        return models[0] if models else None
    except:
        return None

# --- [4] 메인 서비스 로직 ---
def main():
    with st.sidebar:
        st.title("🎛️ Controller")
        if 'auth_user' not in st.session_state:
            key = st.text_input("License Key", type="password")
            if st.button("Login"):
                if key in st.session_state.user_db:
                    st.session_state.auth_user = key
                    st.rerun()
                else: st.error("키가 올바르지 않습니다.")
            return

        user = st.session_state.user_db[st.session_state.auth_user]
        st.subheader(f"💎 {user['plan']} Member")
        st.progress(user['usage'] / user['limit'])
        
        # 현재 연결된 엔진 확인
        engine = get_available_engine()
        st.success(f"Engine: {engine}")
        
        if st.button("Logout"):
            del st.session_state.auth_user
            st.rerun()

    st.title("Pick & Shot 📸 : AI Studio")
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("1. Pick 소재")
        file = st.file_uploader("상품 이미지 업로드", type=['jpg', 'png', 'jpeg'])
        vibe = st.selectbox("브랜드 감성", ["Hermes Minimal", "Cyberpunk Future", "Aesop Nature"])
        shot_btn = st.button("🚀 Shot (전략 생성)")

    with col2:
        st.subheader("2. View")
        if file:
            img = Image.open(file)
            st.image(img, use_column_width=True)

    if shot_btn and file:
        if not engine:
            st.error("API Key 또는 라이브러리 설정 오류입니다.")
            return

        with st.status("🧠 BCG 전략팀 분석 중...", expanded=True) as status:
            try:
                model = genai.GenerativeModel(engine)
                prompt = f"""
                You are a BCG Senior Strategist and a Luxury Brand Creative Director.
                Analyze the product and provide a 7-star commercial strategy.
                Target Vibe: {vibe}
                
                [Output]
                1. Strategic Concept (Korean)
                2. Visual Direction (Korean)
                3. High-End Image Generation Prompt (English)
                """
                response = model.generate_content([prompt, img])
                
                st.session_state.user_db[st.session_state.auth_user]['usage'] += 1
                status.update(label="✅ 전략 완성", state="complete")
                
                st.divider()
                st.subheader("📋 Strategy Report")
                st.markdown(f'<div class="report-box">{response.text}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
