import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- [1] BCG & VOGUE 스타일링 (다크 모드 고정) ---
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
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #FF4B4B, #FF9966); }
</style>
""", unsafe_allow_html=True)

# --- [2] 데이터베이스 (SaaS 라이선스 시스템) ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "BASIC-1234": {"plan": "BASIC", "usage": 0, "limit": 30},
        "PRO-5678":   {"plan": "PRO",   "usage": 0, "limit": 100},
        "PREM-9999":  {"plan": "PREMIUM", "usage": 0, "limit": 300}
    }

# --- [3] 천재 디버거 로직: 엔진 자동 탐색 ---
def get_best_engine():
    """404 에러 방지: 내 API 키가 지원하는 최적의 엔진을 자동으로 찾습니다."""
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        # 서버에서 사용 가능한 모델 리스트 확보
        models = [m.name.replace('models/', '') for m in genai.list_models() 
                  if 'generateContent' in m.supported_generation_methods]
        
        # 선호도 순위: 1.5 Flash -> 1.5 Pro -> Pro Vision -> Pro
        priority = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro-vision', 'gemini-pro']
        for p in priority:
            if p in models: return p
        return models[0] if models else None
    except:
        return None

# --- [4] BCG 기획자 로직: 하이앤드 전략 수립 ---
def generate_strategy(image, vibe, engine):
    model = genai.GenerativeModel(engine)
    
    # 픽앤샷만의 독보적인 프롬프트 엔지니어링
    system_prompt = f"""
    You are a BCG Senior Strategist and a Creative Director for a Luxury Fashion Brand.
    Analyze the product in the image and provide a 7-star commercial strategy.
    
    Target Vibe: {vibe}
    
    [Output Structure]
    1. **Strategic Concept (Korean):** Brand positioning and emotional trigger.
    2. **Target Audience (Korean):** Deep psychological profile of the buyer.
    3. **Visual Direction (Korean):** Detailed lighting, composition, and props.
    4. **Image Generation Prompt (English):** A master-level prompt for DALL-E 3. 
       (Must include camera settings, lighting type, and 8k cinematic details.)
    """
    
    try:
        # 모델 종류에 따라 입력 방식 대응
        response = model.generate_content([system_prompt, image])
        return response.text
    except Exception as e:
        return f"전략 수립 중 오류 발생: {str(e)}"

# --- [5] 메인 UI 구성 ---
def main():
    # 사이드바: 컨트롤 타워
    with st.sidebar:
        st.title("🎛️ Control Center")
        
        if 'auth_user' not in st.session_state:
            key = st.text_input("License Key", type="password")
            if st.button("Login"):
                if key in st.session_state.user_db:
                    st.session_state.auth_user = key
                    st.rerun()
                else: st.error("Invalid Key")
            return

        # 로그인 성공 후 정보 표시
        user = st.session_state.user_db[st.session_state.auth_user]
        st.subheader(f"💎 {user['plan']} Member")
        st.progress(user['usage'] / user['limit'])
        st.caption(f"Usage: {user['usage']} / {user['limit']} shots")
        
        # [자동 엔진 확인]
        current_engine = get_best_engine()
        st.success(f"Connected: {current_engine}")
        
        if st.button("Logout"):
            del st.session_state.auth_user
            st.rerun()

    # 메인 대시보드
    st.title("Pick & Shot 📸 : AI Studio")
    st.markdown("### High-End Product Photography Strategy")

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.markdown("#### 1. Material (Pick)")
        file = st.file_uploader("Upload Product Image", type=['jpg', 'png', 'jpeg'])
        vibe = st.selectbox("Brand Vibe", ["Hermes Minimal", "Cyberpunk Future", "Aesop Nature", "Vogue Noir"])
        
        shot_btn = st.button("🚀 Shot (Generate Strategy)")

    with col2:
        st.markdown("#### 2. Preview")
        if file:
            st.image(file, use_column_width=True, caption="Original Material")
            img = Image.open(file)

    # 실행 및 결과 출력
    if shot_btn and file:
        if current_engine:
            with st.status("🧠 AI 기획팀 가동 중...", expanded=True) as status:
                status.write("BCG 전략가가 시장을 분석 중입니다...")
                result = generate_strategy(img, vibe, current_engine)
                
                # 사용량 업데이트
                st.session_state.user_db[st.session_state.auth_user]['usage'] += 1
                status.update(label="✅ 기획 리포트 완성", state="complete")

            st.divider()
            st.subheader("📋 Creative Strategy Report")
            st.markdown(f'<div class="report-box">{result}</div>', unsafe_allow_html=True)
            
            # 프롬프트만 따로 복사하기 쉽게 제공
            st.subheader("🎨 AI Image Prompt")
            st.code(result.split("Prompt")[-1].strip() if "Prompt" in result else "분석 결과 참고")
        else:
            st.error("연결된 AI 엔진이 없습니다. API 키를 확인하세요.")

if __name__ == "__main__":
    main()
