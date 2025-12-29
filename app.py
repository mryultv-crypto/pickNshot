import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1] Anti-Gravity & High-End 설정 ---
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
    div.stButton > button:hover { transform: translateY(-2px); }
    .report-box { 
        background-color: #1E1E1E; padding: 25px; border-radius: 12px; 
        border: 1px solid #333; margin-bottom: 20px; color: #eee; line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# --- [2] 핵심 엔진: 개발자님의 해결책 적용 (동적 모델 할당) ---
def get_dynamic_engine():
    """
    [개발자님 솔루션 적용]
    하드코딩된 이름을 쓰지 않고, 현재 API 키가 볼 수 있는 
    '실제 모델 리스트'를 조회하여 가장 최신 모델을 자동으로 선택합니다.
    """
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        # 1. 서버에 존재하는 모델 리스트 싹 긁어오기
        all_models = [m.name for m in genai.list_models() 
                      if 'generateContent' in m.supported_generation_methods]
        
        # 2. 우선순위 로직 (개발자님이 발견하신 2.0, 2.5 등 최신 모델 우선 탐색)
        # 리스트에 있는 것 중 'flash'나 'pro'가 들어간 모델을 찾음
        target_model = None
        
        # (1) 최신 플래시 모델 탐색 (2.5 -> 2.0 -> 1.5)
        for m in all_models:
            if 'flash' in m and ('2.5' in m or '2.0' in m):
                return m # 최신 발견 즉시 반환
        
        # (2) 1.5 플래시 탐색
        for m in all_models:
            if 'flash' in m and '1.5' in m:
                return m

        # (3) 그 외 아무 프로 모델이나 탐색
        for m in all_models:
            if 'pro' in m:
                return m
                
        # (4) 정 없으면 리스트의 첫 번째 놈이라도 잡음
        return all_models[0] if all_models else None

    except Exception as e:
        return None

# --- [3] 메인 UI: Anti-Gravity ---
def main():
    # 사이드바: 엔진 상태 확인
    with st.sidebar:
        st.title("🎛️ System Status")
        
        engine = get_dynamic_engine()
        
        if engine:
            # 모델명에서 'models/' 제거하고 깔끔하게 표시
            clean_name = engine.replace('models/', '')
            st.success(f"✅ AI Engine Active\n\n[{clean_name}]")
            st.info("개발자님이 발견하신 최신 모델로\n자동 연결되었습니다.")
        else:
            st.error("❌ 연결 실패\nAPI Key를 확인해주세요.")

    # 메인 화면
    st.title("Pick & Shot 📸 : Anti-Gravity")
    st.markdown("##### The Next Generation AI Studio")

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("1. Material Pick")
        file = st.file_uploader("상품 이미지 업로드", type=['jpg', 'png', 'jpeg'])
        
        # 안티그레비티 전용 무드
        vibe = st.selectbox("Shooting Concept", 
                           ["Anti-Gravity (Zero Gravity)", "Levitation (Floating Object)", 
                            "Future Tech (Cyber)", "Luxury Minimal"])
        
        shot_btn = st.button("🚀 SHOT (Generate)")

    with col2:
        st.subheader("2. Live Preview")
        if file:
            img = Image.open(file)
            st.image(img, use_column_width=True)

    # 실행 로직
    if shot_btn and file and engine:
        with st.status(f"🧠 [{engine.replace('models/','')}] 엔진 가동 중...", expanded=True) as status:
            try:
                model = genai.GenerativeModel(engine)
                
                # 안티그레비티 전용 프롬프트
                prompt = f"""
                You are the Creative Director of 'Anti-Gravity', a futuristic design studio.
                Analyze the uploaded product image and create a visual strategy.
                Target Concept: {vibe}
                
                [OUTPUT FORMAT]
                1. **Conceptual Strategy (Korean):** Explain how to express the '{vibe}' concept with this product. Focus on floating, weightlessness, or futuristic elements.
                2. **Lighting & Composition (Korean):** Describe lighting (e.g., Neon rim light, Softbox) and angles (e.g., Low angle, Floating view).
                3. **Image Generation Prompt (English):** A detailed prompt for DALL-E 3. 
                   (Keywords: Zero gravity, floating, suspended in air, cinematic lighting, 8k resolution, photorealistic).
                """
                
                response = model.generate_content([prompt, img])
                status.update(label="✅ 기획안 생성 완료!", state="complete")
                
                st.divider()
                st.subheader("📋 Anti-Gravity Strategy Report")
                st.markdown(f'<div class="report-box">{response.text}</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"생성 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
