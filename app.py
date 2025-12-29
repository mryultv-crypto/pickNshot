import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import time

# --- [1] 페이지 설정 ---
st.set_page_config(page_title="Pick & Shot: Pro Studio", page_icon="📸", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    section[data-testid="stSidebar"] { background-color: #1c1e24; }
    .stButton>button {
        width: 100%; background-color: #FF4B4B; color: white; 
        border-radius: 8px; height: 55px; font-weight: 800; font-size: 18px; border: none;
    }
    .stButton>button:hover { background-color: #FF2B2B; color: white; }
    .report-box {
        background-color: #262730; padding: 25px; border-radius: 10px; 
        border-left: 5px solid #FF4B4B; margin-bottom: 20px; line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# --- [2] API 설정 ---
def configure_genai():
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("🚨 API Key가 없습니다. Secrets 설정을 확인하세요.")
            return False
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"⚠️ 설정 오류: {str(e)}")
        return False

# --- [3] 분석 로직 (하이브리드) ---
def analyze_hybrid(product_img, model_img, vibe):
    model = genai.GenerativeModel('gemini-pro')
    
    base_prompt = f"""
    당신은 세계 최고의 광고 디렉터입니다. 
    이미지를 분석해 '{vibe}' 컨셉의 기획안과 프롬프트를 작성하세요.
    [필수] 1. 상품의 로고/재질 변형 금지. 2. 조명/앵글의 전문적 묘사.
    """

    if model_img: 
        specific = " [합성] 모델 이미지의 인물 특징을 유지하며 상품을 착용/사용하는 컷 연출."
        content = [base_prompt + specific, product_img, model_img]
    else: 
        specific = " [가상 캐스팅] 모델 사진이 없습니다. 상품과 분위기에 딱 맞는 모델을 AI가 추천하여 묘사하세요."
        content = [base_prompt + specific, product_img]

    instruction = """
    \n출력 형식:
    PART 1. [기획안] (한글): 컨셉, 모델 스타일링, 조명 세팅
    PART 2. [프롬프트] (영어): 복사 가능한 Midjourney용 텍스트만 (설명 제외)
    """
    
    if isinstance(content[0], str): content[0] += instruction

    try:
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- [4] 메인 UI ---
def main():
    with st.sidebar:
        st.title("Pick & Shot 📸")
        st.caption("Pro Edition")
        
        st.header("1. Upload")
        p_file = st.file_uploader("📦 상품 (필수)", type=["jpg","png","webp"])
        st.markdown("---")
        m_file = st.file_uploader("bust_in_silhouette: 모델 (선택)", type=["jpg","png","webp"])
        
        st.header("2. Vibe")
        vibe = st.selectbox("분위기", ["Luxury Studio", "Cinematic Film", "Urban Street", "Nature Sunlight"])
        
        st.markdown("---")
        btn = st.button("✨ 생성하기")

    st.markdown("### 🎞️ Preview")
    c1, c2 = st.columns(2)
    p_img, m_img = None, None

    with c1:
        if p_file: 
            p_img = Image.open(p_file)
            st.image(p_img, caption="Product")
        else: st.info("👈 상품 필수")

    with c2:
        if m_file:
            m_img = Image.open(m_file)
            st.image(m_img, caption="Model")
        else:
            st.markdown("<div style='padding:40px; border:2px dashed #555; text-align:center; color:#888;'>모델 없음<br>(AI 자동 추천)</div>", unsafe_allow_html=True)

    if btn:
        if not p_file: st.warning("상품 이미지를 넣어주세요!")
        elif configure_genai():
            with st.spinner("AI가 분석 중입니다..."):
                res = analyze_hybrid(p_img, m_img, vibe)
                st.session_state['res'] = res

    if 'res' in st.session_state:
        st.markdown("---")
        st.markdown(f'<div class="report-box">{st.session_state["res"]}</div>', unsafe_allow_html=True)
        st.code(st.session_state["res"], language="text")

if __name__ == "__main__":
    main()
