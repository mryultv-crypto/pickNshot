import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from datetime import datetime
import time

# --- [1] BCG급 기획 & 보그급 비주얼 설정 ---
st.set_page_config(page_title="Pick & Shot: Enterprise Edition", page_icon="📸", layout="wide")

# 스타일링: 럭셔리 다크 모드 & 가독성 최적화
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    div.stButton > button {
        width: 100%; border-radius: 8px; height: 55px; font-weight: 800; font-size: 18px;
        background: linear-gradient(90deg, #FF4B4B 0%, #FF9966 100%); color: white; border: none;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3); transition: all 0.3s ease;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 75, 75, 0.5); }
    .report-box {
        background-color: #1E1E1E; padding: 25px; border-radius: 12px; 
        border: 1px solid #333; margin-bottom: 20px;
    }
    .badge {
        background-color: #333; color: #eee; padding: 4px 8px; border-radius: 4px; font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)

# --- [2] 데이터베이스 (Mock DB) ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "BASIC-1234": {"plan": "BASIC", "usage": 0, "limit": 30, "last_date": ""},
        "PRO-5678":   {"plan": "PRO",   "usage": 0, "limit": 100, "last_date": ""},
        "PREM-9999":  {"plan": "PREMIUM", "usage": 0, "limit": 300, "last_date": ""}
    }

# --- [3] 핵심 로직: BCG 전략 + 천재 디버깅 ---
def configure_google_api():
    """API 키 로드 및 검증"""
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY")
        if not api_key: return False
        genai.configure(api_key=api_key)
        return True
    except:
        return False

def get_gemini_response(content, vibe):
    """
    [천재 디버깅 로직]
    1순위: 최신 1.5 Flash 모델 시도
    2순위: 실패 시 안정적인 Pro Vision 모델로 자동 전환
    """
    system_instruction = f"""
    You are the Creative Director of a top-tier global advertising agency (like Ogilvy or BBDO).
    Your goal is to analyze the product image and create a 'High-End Visual Strategy'.
    
    Current Concept Vibe: {vibe}
    
    [OUTPUT FORMAT]
    1. **Creative Concept (Korean):** - Define the core message and tone.
       - Describe the target audience and psychological trigger.
    
    2. **Visual Direction (Korean):**
       - Lighting (e.g., Rembrandt, Butterfly, Soft/Hard).
       - Color Palette (Hex codes or descriptions).
       - Camera Angle & Composition (Rule of thirds, Low angle, etc.).
       
    3. **Generative AI Prompt (English - STRICTLY for DALL-E 3 / Midjourney):**
       - Create a highly detailed, descriptive prompt.
       - Include: Subject details, Environment, Lighting, Camera lens (e.g., 85mm f1.8), Film stock (e.g., Kodak Portra 400), and Style modifiers (e.g., 8k, photorealistic, cinematic lighting).
       - DO NOT include explanatory text in this section, just the prompt.
    """
    
    # 입력 데이터 포맷팅 (텍스트 + 이미지)
    final_content = [system_instruction, content[0]] # [프롬프트, 이미지]
    
    # 1차 시도: 최신 모델 (Gemini 1.5 Flash)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(final_content)
        return response.text, "Gemini 1.5 Flash (Latest)"
    except Exception as e:
        # 2차 시도: 안정형 모델 (Gemini Pro Vision) - 404 오류 시 여기로 넘어옴
        try:
            model = genai.GenerativeModel('gemini-pro-vision')
            response = model.generate_content(final_content)
            return response.text, "Gemini Pro Vision (Stable)"
        except Exception as e2:
            return f"Error: 모든 AI 모델 연결 실패. API 키를 확인하거나 잠시 후 다시 시도하세요.\n({str(e2)})", "Error"

# --- [4] 메인 UI (SaaS 스타일) ---
def main():
    # 사이드바: 로그인 및 상태창
    with st.sidebar:
        st.title("🎛️ Controller")
        
        if 'auth_user' not in st.session_state:
            input_key = st.text_input("License Key", type="password")
            if st.button("Login"):
                if input_key in st.session_state.user_db:
                    st.session_state['auth_user'] = input_key
                    st.success("Access Granted")
                    st.rerun()
                else:
                    st.error("Invalid Key")
            st.info("Demo Keys: BASIC-1234, PRO-5678")
            return
        
        # 로그인 후 상태창
        user = st.session_state.user_db[st.session_state['auth_user']]
        usage_percent = (user['usage'] / user['limit'])
        
        st.markdown(f"### {user['plan']} Member")
        st.progress(usage_percent)
        st.caption(f"Usage: {user['usage']} / {user['limit']} shots")
        
        if st.button("Logout"):
            del st.session_state['auth_user']
            st.rerun()

    # 메인 화면
    st.title("Pick & Shot 📸 : Enterprise")
    st.markdown("##### The Ultimate AI Commercial Photography Studio")
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown("### 1. Pick (Material)")
        p_file = st.file_uploader("Upload Product Image", type=['png','jpg','jpeg'])
        vibe = st.selectbox("Select Vibe", 
                           ["Luxury Minimal (Hermes Style)", 
                            "Neon Cyberpunk (Tech Style)", 
                            "Natural Sunlight (Aesop Style)", 
                            "Cinematic Noir (Movie Style)"])
        
        generate_btn = st.button("🚀 Shot (Generate)")

    with col2:
        st.markdown("### 2. Preview")
        if p_file:
            st.image(p_file, caption="Original Product", use_column_width=True)
        else:
            st.info("좌측에서 상품 이미지를 업로드해주세요.")

    # 실행 로직
    if generate_btn and p_file:
        if user['usage'] >= user['limit']:
            st.error("🚫 일일 한도를 초과했습니다. 플랜을 업그레이드하세요.")
        elif configure_google_api():
            # UI: 진행바 및 상태 메시지
            status_box = st.status("📸 스튜디오 세팅 중...", expanded=True)
            p_img = Image.open(p_file)
            
            # Step 1: AI 분석 (BCG Strategy)
            status_box.write("🧠 1. 상품 분석 및 비주얼 전략 수립 중 (Creative Director Mode)...")
            result_text, model_used = get_gemini_response([p_img], vibe)
            
            if "Error" in model_used:
                status_box.update(label="🚨 오류 발생", state="error")
                st.error(result_text)
            else:
                # Step 2: 결과 출력
                status_box.write(f"✅ 분석 완료! (Used Model: {model_used})")
                status_box.update(label="✨ 작업 완료!", state="complete")
                
                # 사용량 차감
                st.session_state.user_db[st.session_state['auth_user']]['usage'] += 1
                
                # 결과 리포트
                st.divider()
                st.subheader("📋 Creative Strategy Report")
                st.markdown(f'<div class="report-box">{result_text}</div>', unsafe_allow_html=True)
                
                # 프롬프트 추출 (마지막 문단이 프롬프트일 확률이 높음)
                st.subheader("🎨 Image Generation Prompt")
                st.info("아래 텍스트를 복사하여 DALL-E 3 또는 Midjourney에 붙여넣으세요. (자동 생성 기능 준비 중)")
                st.code(result_text.split("Generative AI Prompt")[-1], language='english')
                
        else:
            st.error("API Key 설정 오류. secrets.toml을 확인하세요.")

if __name__ == "__main__":
    main()
