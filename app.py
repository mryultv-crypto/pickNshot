import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- [1] 페이지 및 스타일 설정 ---
st.set_page_config(page_title="Pick & Shot: Enterprise", page_icon="📸", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    div.stButton > button {
        width: 100%; border-radius: 8px; height: 55px; font-weight: 800; font-size: 18px;
        background: linear-gradient(90deg, #FF4B4B 0%, #FF9966 100%); color: white; border: none;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3); transition: all 0.3s ease;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 75, 75, 0.5); }
    .report-box {
        background-color: #1E1E1E; padding: 25px; border-radius: 12px; 
        border: 1px solid #333; margin-bottom: 20px; color: #eee;
    }
    h1, h2, h3 { color: #fff !important; }
    p, li, .stMarkdown { color: #ccc !important; }
</style>
""", unsafe_allow_html=True)

# --- [2] 데이터베이스 (Mock) ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "BASIC-1234": {"plan": "BASIC", "usage": 0, "limit": 30},
        "PRO-5678":   {"plan": "PRO",   "usage": 0, "limit": 100},
        "PREM-9999":  {"plan": "PREMIUM", "usage": 0, "limit": 300}
    }

# --- [3] 핵심 로직 (안전 모드) ---
def configure_google_api():
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY")
        if not api_key: return False
        genai.configure(api_key=api_key)
        return True
    except:
        return False

def get_gemini_response(image, vibe):
    """
    [안전 모드 엔진]
    오류가 나는 신형 모델 대신, 구형 환경에서도 100% 작동하는
    'gemini-pro-vision'을 강제로 사용합니다.
    """
    prompt = f"""
    You are the Creative Director of a top-tier global advertising agency.
    Analyze this product image and create a high-end visual strategy.
    
    Target Vibe: {vibe}
    
    [OUTPUT FORMAT]
    1. **Creative Concept (Korean):** Core message, tone, target audience.
    2. **Visual Direction (Korean):** Lighting, Color, Angles.
    3. **Generative AI Prompt (English):** Detailed prompt for DALL-E 3 (No explanations, just prompt).
    """
    
    # gemini-pro-vision은 [프롬프트, 이미지] 순서의 리스트가 필수입니다.
    inputs = [prompt, image]
    
    try:
        # 무조건 작동하는 안전 모델 사용
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content(inputs)
        return response.text, "Gemini Pro Vision (Stable)"
    except Exception as e:
        return f"Error: {str(e)}\n(Tip: API 키가 올바른지 확인해주세요.)", "Fail"

# --- [4] 메인 UI ---
def main():
    with st.sidebar:
        st.title("🎛️ Controller")
        
        # 버전 확인용 (디버깅)
        st.caption(f"Engine Ver: {genai.__version__}")
        
        if 'auth_user' not in st.session_state:
            input_key = st.text_input("License Key", type="password")
            if st.button("Login"):
                if input_key in st.session_state.user_db:
                    st.session_state['auth_user'] = input_key
                    st.rerun()
                else:
                    st.error("Invalid Key")
            st.info("Demo: PRO-5678")
            return
        
        user = st.session_state.user_db[st.session_state['auth_user']]
        st.metric(label=f"{user['plan']}", value=f"{user['usage']}/{user['limit']}")
        if st.button("Logout"):
            del st.session_state['auth_user']
            st.rerun()

    st.title("Pick & Shot 📸 : Enterprise")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Pick (Upload)")
        p_file = st.file_uploader("상품 이미지", type=['png','jpg','jpeg'])
        vibe = st.selectbox("Vibe", ["Luxury Minimal", "Neon Cyberpunk", "Natural Sunlight"])
        generate_btn = st.button("🚀 Shot (Generate)")

    with col2:
        st.subheader("2. Preview")
        if p_file:
            st.image(p_file, use_column_width=True)
            p_img = Image.open(p_file)

    if generate_btn and p_file:
        if configure_google_api():
            with st.status("📸 AI 분석 중...", expanded=True) as status:
                res_text, model_name = get_gemini_response(p_img, vibe)
                
                if model_name == "Fail":
                    status.update(label="🚨 오류", state="error")
                    st.error(res_text)
                else:
                    status.update(label="✅ 완료!", state="complete")
                    st.success(f"Success! Engine: {model_name}")
                    st.session_state.user_db[st.session_state['auth_user']]['usage'] += 1
                    st.divider()
                    st.subheader("📋 Creative Strategy Report")
                    st.markdown(f'<div class="report-box">{res_text}</div>', unsafe_allow_html=True)
        else:
            st.error("API Key 설정이 필요합니다.")

if __name__ == "__main__":
    main()
