import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

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

# --- [2] SaaS 라이선스 시스템 ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "BASIC-1234": {"plan": "BASIC", "usage": 0, "limit": 30},
        "PRO-5678":   {"plan": "PRO",   "usage": 0, "limit": 100},
        "PREM-9999":  {"plan": "PREMIUM", "usage": 0, "limit": 300}
    }

# --- [3] 천재 디버거의 오류 회피 로직 ---
def get_best_model(vibe, image):
    """
    내 API 키가 허용하는 가장 똑똑한 모델을 자동으로 찾아 기획안을 작성합니다.
    """
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        # [핵심] 사용 가능한 모델 리스트를 서버에 직접 물어봄 (404 원천 차단)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 우선순위: 1.5-flash -> 1.0-pro-vision
        target_model = ""
        if 'models/gemini-1.5-flash' in available_models: target_model = 'gemini-1.5-flash'
        elif 'models/gemini-pro-vision' in available_models: target_model = 'gemini-pro-vision'
        else: target_model = available_models[0].split('/')[-1]

        model = genai.GenerativeModel(target_model)
        
        # BCG급 하이엔드 프롬프트
        prompt = f"""
        You are a BCG Senior Strategist and a Creative Director for a Luxury Brand.
        Analyze this product and provide a 7-star commercial strategy.
        Target Vibe: {vibe}
        
        [OUTPUT]
        1. **Strategic Concept (Korean):** Brand positioning and emotional hook.
        2. **Visual Direction (Korean):** Professional lighting, color palette, and composition.
        3. **Image Generation Prompt (English):** Master-level prompt for DALL-E 3 (8k, cinematic lighting).
        """
        
        response = model.generate_content([prompt, image])
        return response.text, target_model
    except Exception as e:
        return f"치명적 오류 발생: {str(e)}", "Fail"

# --- [4] 메인 UI ---
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
        if st.button("Logout"):
            del st.session_state.auth_user
            st.rerun()

    st.title("Pick & Shot 📸 : AI Studio")
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("1. Pick Material")
        file = st.file_uploader("상품 이미지 업로드", type=['jpg', 'png', 'jpeg'])
        vibe = st.selectbox("브랜드 감성", ["Luxury Minimal", "Cyberpunk Future", "Aesop Nature"])
        shot_btn = st.button("🚀 Shot (Generate Strategy)")

    with col2:
        st.subheader("2. Preview")
        if file:
            img = Image.open(file)
            st.image(img, use_column_width=True)

    if shot_btn and file:
        with st.status("🧠 AI 기획팀이 전략 수립 중...", expanded=True) as status:
            res, engine = get_best_model(vibe, img)
            if engine == "Fail":
                status.update(label="🚨 오류 발생", state="error")
                st.error(res)
            else:
                status.update(label=f"✅ 완료 (Engine: {engine})", state="complete")
                st.session_state.user_db[st.session_state.auth_user]['usage'] += 1
                st.divider()
                st.subheader("📋 Creative Strategy Report")
                st.markdown(f'<div class="report-box">{res}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
