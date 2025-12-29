import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- [1] BCG & VOGUE 하이엔드 스타일 ---
st.set_page_config(page_title="Pick & Shot: Truth", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# --- [2] 진실 확인 로직 (디버깅) ---
def init_and_check():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        # 서버에서 사용 가능한 모델 목록을 강제로 긁어옵니다.
        models = [m.name.replace('models/', '') for m in genai.list_models() 
                  if 'generateContent' in m.supported_generation_methods]
        return models, genai.__version__
    except Exception as e:
        return [f"연결 오류: {str(e)}"], "Unknown"

# --- [3] 메인 프로그램 ---
def main():
    models, ver = init_and_check()
    
    with st.sidebar:
        st.title("🎛️ 시스템 진단")
        st.error(f"라이브러리 버전: {ver}")
        st.write("내 API 키가 지원하는 모델 목록:")
        st.code(models) # 여기서 gemini-1.5-flash가 있는지 확인하세요.

    st.title("Pick & Shot 📸 : Enterprise")
    
    if "연결 오류" in models[0]:
        st.error("API 키 설정을 확인해주세요.")
        return

    col1, col2 = st.columns(2)
    with col1:
        file = st.file_uploader("상품 이미지 업로드", type=['jpg', 'png', 'jpeg'])
        # 목록 중 가장 똑똑한 녀석을 자동 선택 (1.5-flash 우선)
        target = 'gemini-1.5-flash' if 'gemini-1.5-flash' in models else models[0]
        vibe = st.selectbox("브랜드 감성", ["Luxury Minimal", "Cyberpunk", "Aesop Nature"])
        btn = st.button("🚀 광고 기획 리포트 생성")

    if btn and file:
        img = Image.open(file)
        with st.status(f"🧠 {target} 엔진 분석 중...") as status:
            try:
                model = genai.GenerativeModel(target)
                prompt = f"너는 BCG 전략가이자 광고 감독이야. 이 상품의 {vibe} 스타일 광고 기획안을 작성해줘."
                response = model.generate_content([prompt, img])
                st.subheader("📋 Creative Strategy Report")
                st.write(response.text)
                status.update(label="✅ 완료", state="complete")
            except Exception as e:
                st.error(f"실행 오류: {e}")

if __name__ == "__main__":
    main()
