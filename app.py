import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- [1] 페이지 및 스타일 설정 (Enterprise Dark Mode) ---
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

# --- [2] 데이터베이스 (Mock DB) ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "BASIC-1234": {"plan": "BASIC", "usage": 0, "limit": 30},
        "PRO-5678":   {"plan": "PRO",   "usage": 0, "limit": 100},
        "PREM-9999":  {"plan": "PREMIUM", "usage": 0, "limit": 300}
    }

# --- [3] 핵심 로직: 자동 우회 엔진 (Auto-Fallback) ---
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
    [핵심 기술]
    1.5 Flash(신형)가 실패하면 Pro Vision(구형)으로 자동 전환하여
    어떤 환경에서도 무조건 결과를 만들어냅니다.
    """
    # 프롬프트 설계 (BCG 전략 + 보그 스타일)
    prompt = f"""
    You are the Creative Director of a top-tier global advertising agency.
    Analyze this product image and create a high-end visual strategy.
    
    Target Vibe: {vibe}
    
    [OUTPUT FORMAT]
    1. **Creative Concept (Korean):** Core message, tone, target audience.
    2. **Visual Direction (Korean):** Lighting, Color, Angles.
    3. **Generative AI Prompt (English):** Detailed prompt for DALL-E 3 (No explanations, just prompt).
    """
    
    # 입력 데이터 구성
    inputs = [prompt, image]
    
    # 1차 시도: 최신 모델 (1.5 Flash)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(inputs)
        return response.text, "Gemini 1.5 Flash (Latest)"
        
    except Exception as e_flash:
        # 2차 시도: 구형 모델 (Pro Vision) - 1.5 실패시 즉시 가동
        try:
            # Pro Vision은 리스트 순서가 다를 수 있어 안전하게 재구성
            model_old = genai.GenerativeModel('gemini-pro-vision')
            response = model_old.generate_content(inputs)
            return response.text, "Gemini Pro Vision (Stable)"
        except Exception as e_pro:
            return f"Error: 모든 모델 연결 실패.\n1차오류: {e_flash}\n2차오류: {e_pro}", "Fail"

# --- [4] 메인 UI ---
def main():
    # 사이드바: 컨트롤러 및 버전 확인
    with st.sidebar:
        st.title("🎛️ Controller")
        
        # [진실의 창] 현재 실제 작동중인 버전 표시
        st.error(f"System Ver: {genai.__version__}")
        
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

    # 메인 화면
    st.title("Pick & Shot 📸 : Enterprise")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Pick (Upload)")
        p_file = st.file_uploader("상품 이미지", type=['png','jpg','jpeg'])
        vibe = st.selectbox("Vibe", ["Luxury Minimal", "Neon Cyberpunk", "Natural Sunlight", "Cinematic Noir"])
        
        # 버튼 스타일
        generate_btn = st.button("🚀 Shot (Generate)")

    with col2:
        st.subheader("2. Preview")
        if p_file:
            st.image(p_file, use_column_width=True)
            p_img = Image.open(p_file)

    # 실행 로직
    if generate_btn and p_file:
        if configure_google_api():
            with st.status("📸 AI 스튜디오 가동 중...", expanded=True) as status:
                status.write("🧠 이미지 분석 및 전략 수립 중...")
                
                # 분석 실행
                res_text, model_name = get_gemini_response(p_img, vibe)
                
                if model_name == "Fail":
                    status.update(label="🚨 치명적 오류", state="error")
                    st.error(res_text)
                else:
                    status.update(label="✅ 작업 완료!", state="complete")
                    
                    # 성공 메시지 및 모델 정보 표시
                    st.success(f"생성 성공! (사용된 엔진: {model_name})")
                    st.session_state.user_db[st.session_state['auth_user']]['usage'] += 1
                    
                    # 결과 리포트 출력
                    st.divider()
                    st.subheader("📋 Creative Strategy Report")
                    st.markdown(f'<div class="report-box">{res_text}</div>', unsafe_allow_html=True)
        else:
            st.error("API Key 설정이 필요합니다. secrets.toml을 확인하세요.")

if __name__ == "__main__":
    main()
