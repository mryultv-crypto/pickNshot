import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- [1] BCG & VOGUE 하이엔드 디자인 설정 ---
st.set_page_config(page_title="Pick & Shot: Enterprise", page_icon="📸", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    div.stButton > button {
        width: 100%; border-radius: 8px; height: 55px; font-weight: 800; font-size: 18px;
        background: linear-gradient(90deg, #FF4B4B 0%, #FF9966 100%); color: white; border: none;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
    }
    .report-box {
        background-color: #1E1E1E; padding: 25px; border-radius: 12px; 
        border: 1px solid #333; margin-bottom: 20px; color: #eee;
    }
</style>
""", unsafe_allow_html=True)

# --- [2] SaaS 라이선스 및 사용량 DB ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "BASIC-1234": {"plan": "BASIC", "usage": 0, "limit": 30},
        "PRO-5678":   {"plan": "PRO",   "usage": 0, "limit": 100},
        "PREM-9999":  {"plan": "PREMIUM", "usage": 0, "limit": 300}
    }

# --- [3] 핵심 엔진: 404 오류 자동 회복 로직 ---
def get_ai_response(image, vibe):
    """
    1.5 Flash를 우선 시도하되, 실패 시 1.0 Pro 모델로 자동 전환하여 
    어떤 상황에서도 결과(기획안)를 뽑아냅니다.
    """
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        # 픽앤샷 전용 하이엔드 프롬프트 (BCG 전략가 모드)
        prompt = f"""
        You are a BCG Senior Strategist and a Creative Director for a Luxury Brand.
        Analyze this product and provide a 7-star commercial strategy.
        Target Vibe: {vibe}
        
        [OUTPUT]
        1. **Strategic Concept (Korean):** Brand positioning.
        2. **Visual Direction (Korean):** Lighting, Color, Angles.
        3. **Image Generation Prompt (English):** Master-level prompt for DALL-E 3.
        """
        
        # 1차 시도: 최신 1.5 Flash
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([prompt, image])
            return response.text, "Gemini 1.5 Flash"
        except:
            # 2차 시도: 안정적인 Pro Vision (404 발생 시 이쪽으로 우회)
            model = genai.GenerativeModel('gemini-pro-vision')
            response = model.generate_content([prompt, image])
            return response.text, "Gemini Pro Vision (Stable Mode)"
            
    except Exception as e:
        return f"치명적 오류: {str(e)}", "Fail"

# --- [4] 메인 UI (로그인 및 서비스 화면) ---
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
            st.info("Demo: PRO-5678")
            return

        # 로그인 성공 시 유저 정보
        user = st.session_state.user_db[st.session_state.auth_user]
        st.subheader(f"💎 {user['plan']} PLAN")
        st.progress(user['usage'] / user['limit'])
        st.caption(f"Usage: {user['usage']} / {user['limit']} shots")
        
        if st.button("Logout"):
            del st.session_state.auth_user
            st.rerun()

    # 서비스 메인 화면
    st.title("Pick & Shot 📸 : AI Studio")
    st.markdown("##### The Ultimate High-End Product Strategy Solution")

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("1. Pick Material")
        file = st.file_uploader("상품 이미지 업로드", type=['jpg', 'png', 'jpeg'])
        vibe = st.selectbox("브랜드 감성 선택", ["Luxury Minimal", "Cyberpunk Future", "Aesop Nature"])
        shot_btn = st.button("🚀 Shot (광고 기획 시작)")

    with col2:
        st.subheader("2. View")
        if file:
            img = Image.open(file)
            st.image(img, use_column_width=True)

    # 결과 출력
    if shot_btn and file:
        with st.status("🧠 AI 기획팀이 전략을 수립 중입니다...", expanded=True) as status:
            res_text, engine = get_ai_response(img, vibe)
            
            if engine == "Fail":
                status.update(label="🚨 오류 발생", state="error")
                st.error(res_text)
            else:
                status.update(label=f"✅ 기획 완료 (Engine: {engine})", state="complete")
                st.session_state.user_db[st.session_state.auth_user]['usage'] += 1
                
                st.divider()
                st.subheader("📋 Creative Strategy Report")
                st.markdown(f'<div class="report-box">{res_text}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
