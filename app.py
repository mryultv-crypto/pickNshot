import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1] BCG & VOGUE 하이엔드 스타일링 ---
st.set_page_config(page_title="Pick & Shot: Enterprise", page_icon="📸", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    div.stButton > button {
        width: 100%; border-radius: 8px; height: 55px; font-weight: 800; font-size: 18px;
        background: linear-gradient(90deg, #FF4B4B 0%, #FF9966 100%); color: white; border: none;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3); transition: all 0.3s ease;
    }
    .report-box {
        background-color: #1E1E1E; padding: 25px; border-radius: 12px; 
        border: 1px solid #333; margin-bottom: 20px; color: #eee; line-height: 1.6;
        font-family: 'Helvetica', sans-serif;
    }
    .badge {
        background-color: #333; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; margin-right: 5px;
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

# --- [3] 핵심 엔진: 모델 자동 매칭 (404 원천 차단) ---
def get_available_engine():
    """
    사용 가능한 Gemini 모델을 찾아서 반환합니다.
    API 키 오류나 모델 리스팅 실패 시 기본 모델을 반환하여 404를 방지합니다.
    """
    default_model = 'gemini-1.5-flash'
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("❌ API Key가 설정되지 않았습니다.")
            return None

        genai.configure(api_key=api_key)

        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    name = m.name.replace('models/', '')
                    available_models.append(name)
        except:
            pass

        # 선호 순위: 최신 모델 우선
        priority_targets = [
            'gemini-1.5-pro', 'gemini-1.5-flash',
            'gemini-2.0-flash', 'gemini-2.0-flash-exp', 
            'gemini-2.5-flash', 'gemini-pro-vision', 'gemini-pro'
        ]
        
        for target in priority_targets:
            if target in available_models:
                return target

        if available_models: return available_models[0]
        return default_model

    except Exception as e:
        st.error(f"엔진 초기화 중 오류 발생: {e}")
        return default_model

# --- [4] 메인 서비스 로직 ---
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
        
        engine = get_available_engine()
        if engine:
            st.success(f"Engine Connected: {engine}")
        else:
            st.error("Engine Connection Failed")
        
        st.divider()
        if st.button("Logout"):
            del st.session_state.auth_user
            st.rerun()

    st.title("Pick & Shot 📸 : AI Studio")
    st.markdown("##### BCG Strategy x VOGUE Visual Directing System")
    
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("1. Asset Upload")
        with st.container(border=True):
            product_file = st.file_uploader("📦 Product Image (Main Subject)", type=['jpg', 'png', 'jpeg'])
            model_file = st.file_uploader("👤 Model Image (Optional Target)", type=['jpg', 'png', 'jpeg'])
            
        vibe = st.selectbox("Brand Mood", 
            ["Hermes Minimal (럭셔리/미니멀)", 
             "Cyberpunk Future (미래지향/테크)", 
             "Aesop Nature (자연주의/오가닉)", 
             "Vogue Editorial (패션/강렬함)",
             "Apple Commercial (깔끔함/제품강조)"])
             
        shot_btn = st.button("🚀 Shot (전략 및 프롬프트 생성)")

    with col2:
        st.subheader("2. Preview Studio")
        if product_file:
            st.image(product_file, caption="Main Product", width=300)
        if model_file:
            st.image(model_file, caption="Target Model", width=300)
            
    if shot_btn and product_file:
        if not engine:
            st.error("API Key 오류 또는 모델을 찾을 수 없습니다. secrets.toml을 확인해주세요.")
            return

        with st.status("🧠 BCG 전략팀 및 VOGUE 디렉터 회의 중...", expanded=True) as status:
            try:
                model = genai.GenerativeModel(engine)
                
                # 이미지 입력 리스트 구성
                inputs = [product_file]
                if model_file:
                    inputs.append(model_file)
                
                # 이미지 로드 (PIL)
                loaded_inputs = []
                p_img = Image.open(product_file)
                loaded_inputs.append(p_img)
                if model_file:
                    m_img = Image.open(model_file)
                    loaded_inputs.append(m_img)

                # 하이엔드 프롬프트 설계 (업그레이드: 일관성 1000% 강화 버전)
                system_prompt = f"""
                You are the world's most detailed **Product Photographer** and **Midjourney/Flux Prompt Engineer**.
                Your mission is to write a prompt that will generate an image indistinguishable from the uploaded real product.

                **[CRITICAL MISSION]**
                1. **VISUAL CLONING**: You must describe the product in the image with forensic precision.
                   - **Frames**: Exact shape (e.g., 'Square with rounded edges', 'Cat-eye'), Finish (Matte vs Glossy), Color (e.g., 'Jet Black font', 'Cream/Ivory temples').
                   - **Details**: Mention visible text (e.g., 'text on inner temple'), hinge material, lens reflectivity.
                   - **Consistency**: The prompt MUST explicitly state: "The eyeglasses have [Specific Color] front and [Specific Color] arms."
                
                2. **HIGH-END VIBE**: Apply the target vibe '{vibe}' ONLY to the lighting, background, and mood. The product shape MUST NOT be distorted or artistically re-interpreted.

                **[OUTPUT STRUCTURE]**
                Provide the report in the following format:

                ### 1. 🧬 Product DNA Analysis (Korean)
                * "AI가 분석한 상품의 시각적 특징입니다."
                - **Frame Front**: (Color, Shape, Material)
                - **Temples (Arms)**: (Color, Detailed shape)
                - **Key Details**: (Logos, Hinges, etc.)

                ### 2. 📸 Ultra-High-End Prompts (English)
                *Copy & Paste these into your image generator.*

                **Option A: The Commercial Masterpiece (Product Only)**
                > **Prompt**: (Subject: [Exact Product Description]) + (Action: Resting clearly on surface / Floating) + (Environment: {vibe} background, minimal) + (Photography: 8k resolution, phase one camera, 100mm macro lens, sharp focus, ray tracing reflections, ultra-detailed texture) --v 6.0
                > **Negative Prompt**: distorted shape, morphing, wrong colors, abstract, cartoon, illustration, low quality, blurry

                **Option B: The Editorial Campaign (With Model)**
                > **Prompt**: (Subject: A high-fashion model [Describe features from model image if provided, else 'generic luxury model']) wearing ([Exact Product Description]) + (Pose: Professional, confident) + (Environment: {vibe} setting, cinematic lighting) + (Photography: Vogue cover style, depth of field, f/1.8, global illumination) --v 6.0
                > **Negative Prompt**: deformed eyes, hands, bad anatomy, missing glasses details, wrong frame color

                **Option C: The Artistic Vision (Creative)**
                > **Prompt**: ([Exact Product Description]) placed in a surreal {vibe} composition + (Lighting: Volumetric fog, neon rim lights, dramatic shadows) + (Style: Hyper-realism, Unreal Engine 5 render, Octane render) --v 6.0
                """
                
                # 입력 전송 (텍스트 + 이미지들)
                # Gemini는 [Text, Image1, Image2...] 순서로 받음
                content_payload = [system_prompt] + loaded_inputs
                
                response = model.generate_content(content_payload)
                
                st.session_state.user_db[st.session_state.auth_user]['usage'] += 1
                status.update(label="✅ 전략 및 기획안 도출 완료", state="complete")
                
                st.divider()
                st.subheader("📋 Creative Director's Report")
                st.markdown(f'<div class="report-box">{response.text}</div>', unsafe_allow_html=True)
                
                st.info("💡 Tip: 위 영문 프롬프트를 복사하여 Midjourney 또는 Flux 모델에 봍여넣으시면 완벽한 이미지를 얻을 수 있습니다.")
                
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
                if "404" in str(e):
                    st.warning("팁: 모델 연결에 실패했습니다. API 설정을 확인해주세요.")

if __name__ == "__main__":
    main()
