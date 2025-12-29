import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import time

# --- [1] BCG급 기획 & 보그급 비주얼 설정 (다크모드) ---
st.set_page_config(page_title="Pick & Shot: Enterprise Edition", page_icon="📸", layout="wide")

# 스타일링: 럭셔리 다크 모드 & 가독성 최적화
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
    p, li { color: #ccc !important; }
</style>
""", unsafe_allow_html=True)

# --- [2] 데이터베이스 (Mock DB) ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "BASIC-1234": {"plan": "BASIC", "usage": 0, "limit": 30},
        "PRO-5678":   {"plan": "PRO",   "usage": 0, "limit": 100},
        "PREM-9999":  {"plan": "PREMIUM", "usage": 0, "limit": 300}
    }

# --- [3] 핵심 로직: BCG 전략 + 오류 원천 차단 ---
def configure_google_api():
    """API 키 로드 및 검증"""
    try:
        # secrets.toml에서 키를 가져옵니다.
        api_key = st.secrets.get("GOOGLE_API_KEY")
        if not api_key: return False
        genai.configure(api_key=api_key)
        return True
    except:
        return False

def get_gemini_response(content, vibe):
    """
    [천재 디버깅 로직 V2]
    404 오류를 피하기 위해 가장 호환성이 좋은 'gemini-pro-vision'을 우선 사용합니다.
    """
    system_instruction = f"""
    You are the Creative Director of a top-tier global advertising agency.
    Current Concept Vibe: {vibe}
    
    [OUTPUT FORMAT]
    1. **Creative Concept (Korean):** Define the core message, tone, and target audience.
    2. **Visual Direction (Korean):** Lighting, Color Palette, Camera Angle.
    3. **Generative AI Prompt (English):** Highly detailed prompt for DALL-E 3 / Midjourney. 
       (Only the prompt text, no explanations).
    """
    
    # 이미지와 텍스트 결합
    prompt_list = [system_instruction, content[0]]
    
    # 모델 호출 (안정성 최우선)
    try:
        # 1순위: Gemini Pro Vision (구버전 라이브러리에서도 100% 작동)
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content(prompt_list)
        return response.text, "Gemini Pro Vision (Stable)"
    except Exception as e:
        # 2순위: 1.5 Flash (최신 라이브러리용)
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt_list)
            return response.text, "Gemini 1.5 Flash"
        except Exception as e2:
            return f"Error: {str(e)}\n(2차 시도 실패: {str(e2)})", "Fail"

# --- [4] 메인 UI ---
def main():
    # 사이드바
    with st.sidebar:
        st.title("🎛️ Controller")
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
        st.metric(label=f"{user['plan']} PLAN", value=f"{user['usage']}/{user['limit']}")
        if st.button("Logout"):
            del st.session_state['auth_user']
            st.rerun()

    # 메인 화면
    st.title("Pick & Shot 📸 : Enterprise")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Pick (Upload)")
        p_file = st.file_uploader("상품 이미지", type=['png','jpg','jpeg'])
        vibe = st.selectbox("Vibe", ["Luxury Minimal", "Neon Cyberpunk", "Natural Sunlight", "Cinematic Noir"])
        btn = st.button("🚀 Shot (Generate)")

    with col2:
        st.subheader("2. Preview")
        if p_file: st.image(p_file, use_column_width=True)

    # 실행
    if btn and p_file:
        if configure_google_api():
            with st.status("📸 AI 스튜디오 가동 중...", expanded=True) as status:
                status.write("🧠 이미지 분석 및 전략 수립 중...")
                p_img = Image.open(p_file)
                
                # 분석 실행
                res_text, model_name = get_gemini_response([p_img], vibe)
                
                if model_name == "Fail":
                    status.update(label="🚨 오류 발생", state="error")
                    st.error(res_text)
                else:
                    status.update(label="✅ 완료!", state="complete")
                    st.success(f"Success! (Engine: {model_name})")
                    st.session_state.user_db[st.session_state['auth_user']]['usage'] += 1
                    
                    st.divider()
                    st.markdown(f'<div class="report-box">{res_text}</div>', unsafe_allow_html=True)
        else:
            st.error("API Key가 없습니다. secrets.toml을 확인하세요.")

if __name__ == "__main__":
    main()
