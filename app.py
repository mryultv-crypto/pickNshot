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
    h1, h2, h3 { color: #fff !important; }
    .stMarkdown { color: #ccc !important; }
</style>
""", unsafe_allow_html=True)

# --- [2] SaaS 라이선스 시스템 ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "BASIC-1234": {"plan": "BASIC", "usage": 0, "limit": 30},
        "PRO-5678":   {"plan": "PRO",   "usage": 0, "limit": 100},
        "PREM-9999":  {"plan": "PREMIUM", "usage": 0, "limit": 300}
    }

# --- [3] 핵심 엔진: 404 차단 및 자동 모델 매칭 ---
def get_verified_engine():
    """서버에 직접 물어봐서 현재 키로 사용 가능한 가장 똑똑한 모델을 가져옵니다."""
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        # 지원되는 모든 모델 리스트 확보
        models = [m.name.replace('models/', '') for m in genai.list_models() 
                  if 'generateContent' in m.supported_generation_methods]
        
        # 선호 순위: 1.5-flash -> 1.5-pro -> pro-vision
        for preferred in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro-vision']:
            if preferred in models: return preferred
        return models[0] if models else None
    except:
        return None

# --- [4] 메인 UI & BCG 기획 로직 ---
def main():
    # 사이드바 컨트롤러
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
        st.caption(f"Usage: {user['usage']} / {user['limit']} shots")
        
        # [디버깅 정보] 현재 연결된 진짜 엔진 확인
        engine = get_verified_engine()
        st.success(f"Connected: {engine}")
        
        if st.button("Logout"):
            del st.session_state.auth_user
            st.rerun()

    # 메인 대시보드
    st.title("Pick & Shot 📸 : AI Studio")
    st.markdown("##### High-End Product Photography Strategy & Generation")

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("1. 소재 업로드 (Pick)")
        file = st.file_uploader("상품 이미지", type=['jpg', 'png', 'jpeg'])
        vibe = st.selectbox("브랜드 감성", ["Hermes Minimal", "Cyberpunk Future", "Aesop Nature", "Vogue Noir"])
        shot_btn = st.button("🚀 광고 이미지 생성 시작")

    with col2:
        st.subheader("2. 미리보기 (Preview)")
        if file:
            img = Image.open(file)
            st.image(img, use_column_width=True)

    # 실행 및 하이엔드 기획안 도출
    if shot_btn and file:
        if not engine:
            st.error("API Key 또는 라이브러리 설정 오류입니다.")
            return

        with st.status(f"🧠 {engine} 엔진이 전략 수립 중...", expanded=True) as status:
            try:
                model = genai.GenerativeModel(engine)
                # BCG 시니어 전략가 페르소나 주입
                prompt = f"""
                You are a BCG Senior Strategist and a Luxury Brand Creative Director.
                Analyze the uploaded product image and provide a 7-star commercial strategy.
                Target Brand Vibe: {vibe}
                
                [Output Structure]
                1. **Strategic Concept (Korean):** Brand positioning and emotional hook.
                2. **Visual Direction (Korean):** Detailed lighting (e.g., Rembrandt, Softbox), composition, and color palette.
                3. **Master Generation Prompt (English):** A highly descriptive prompt for DALL-E 3 or Midjourney. 
                   Include camera settings (e.g., 85mm f1.8), lighting, and 8k cinematic details.
                """
                response = model.generate_content([prompt, img])
                
                st.session_state.user_db[st.session_state.auth_user]['usage'] += 1
                status.update(label="✅ 기획 리포트 완성", state="complete")
                
                st.divider()
                st.subheader("📋 Creative Strategy Report")
                st.markdown(f'<div class="report-box">{response.text}</div>', unsafe_allow_html=True)
                
                st.subheader("🎨 AI Image Generation Prompt")
                st.code(response.text.split("Prompt")[-1].strip() if "Prompt" in response.text else "전략 본문 참고")
                
            except Exception as e:
                status.update(label="🚨 생성 실패", state="error")
                st.error(f"오류 내용: {str(e)}")

if __name__ == "__main__":
    main()
