# ...existing code...
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import traceback

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
    }
</style>
""", unsafe_allow_html=True)

# 간단한 SaaS 유저 DB
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "BASIC-1234": {"plan": "BASIC", "usage": 0, "limit": 30},
        "PRO-5678":   {"plan": "PRO",   "usage": 0, "limit": 100},
        "PREM-9999":  {"plan": "PREMIUM", "usage": 0, "limit": 300}
    }

# 모델 목록 조회(디버깅용) 및 자동 매칭 함수
def list_models_debug(api_key):
    try:
        genai.configure(api_key=api_key)
        models = list(genai.list_models())
        out = []
        for m in models:
            name = getattr(m, "name", str(m))
            methods = getattr(m, "supported_generation_methods", None) or getattr(m, "supported_methods", None) or []
            methods = [str(x) for x in methods]
            out.append({"name": name, "methods": methods})
        return out
    except Exception as e:
        return {"error": str(e)}

def choose_model(api_key):
    try:
        genai.configure(api_key=api_key)
        models = list(genai.list_models())
        model_info = []
        for m in models:
            name = getattr(m, "name", str(m))
            methods = getattr(m, "supported_generation_methods", None) or getattr(m, "supported_methods", None) or []
            methods = [str(x).lower() for x in methods]
            model_info.append((name, methods))

        # 선호순: 서버 반환 이름(full name)을 기준으로 우선 매칭
        preferred = [
            'models/gemini-1.5-flash', 'models/gemini-1.5-pro',
            'models/gemini-pro-vision', 'models/gemini-pro',
            'models/text-bison-001', 'models/chat-bison-001'
        ]

        # preferred에 있고 generate 관련 메서드가 있는 모델 선택
        for pref in preferred:
            for name, methods in model_info:
                if name == pref and any('generate' in m or 'text' in m or 'chat' in m for m in methods):
                    return name, model_info

        # 그렇지 않으면 methods에 generate 관련 키워드가 있는 첫 모델
        for name, methods in model_info:
            if any('generate' in m or 'text' in m or 'chat' in m for m in methods):
                return name, model_info

        return None, model_info
    except Exception as e:
        return None, [{"error": str(e)}]

# 메인
def main():
    # API 키 획득 (st.secrets 또는 환경변수)
    api_key = None
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except Exception:
        api_key = None

    with st.sidebar:
        st.title("🎛️ Controller")
        st.subheader("Available models")
        if api_key:
            lm = list_models_debug(api_key)
            if isinstance(lm, dict) and lm.get("error"):
                st.error("모델 목록 조회 오류: " + lm["error"])
            else:
                with st.expander("모델 목록 (클릭)", expanded=False):
                    for m in lm:
                        st.write(f"- {m['name']}  —  {m['methods']}")
        else:
            st.info("GOOGLE_API_KEY가 설정되어 있지 않습니다. .streamlit/secrets.toml 또는 환경변수를 확인하세요.")

        if 'auth_user' not in st.session_state:
            key = st.text_input("License Key", type="password")
            if st.button("Login"):
                if key in st.session_state.user_db:
                    st.session_state.auth_user = key
                    st.rerun()
                else:
                    st.error("키가 올바르지 않습니다.")
            return

        user = st.session_state.user_db[st.session_state.auth_user]
        st.subheader(f"💎 {user['plan']} Member")
        st.progress(min(1.0, user['usage'] / max(1, user['limit'])))

        engine, model_info = choose_model(api_key) if api_key else (None, [])
        if engine:
            st.success(f"Engine: {engine}")
        else:
            st.warning("지원 가능한 생성 모델을 찾지 못했습니다. 위 모델 목록을 확인하세요.")

        if st.button("Logout"):
            del st.session_state.auth_user
            st.rerun()

    st.title("Pick & Shot 📸 : AI Studio")
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("1. Pick 소재")
        file = st.file_uploader("상품 이미지 업로드", type=['jpg', 'png', 'jpeg'])
        vibe = st.selectbox("브랜드 감성", ["Hermes Minimal", "Cyberpunk Future", "Aesop Nature"])
        shot_btn = st.button("🚀 Shot (전략 생성)")

    with col2:
        st.subheader("2. View")
        if file:
            try:
                preview = Image.open(file)
                st.image(preview, use_column_width=True)
            except Exception:
                st.text("이미지 미리보기 실패.")

    if shot_btn and file:
        if not api_key:
            st.error("GOOGLE_API_KEY가 설정되어 있지 않습니다.")
            return

        engine, model_info = choose_model(api_key)
        if not engine:
            st.error("지원 가능한 모델이 없습니다. 사이드바의 모델 목록을 확인하세요.")
            return

        with st.status("🧠 BCG 전략팀 분석 중...", expanded=True) as status:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(engine)

                # 이미지 바이트를 함께 전송 (멀티모달 지원 모델인 경우)
                img = Image.open(file)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                image_bytes = buf.getvalue()

                # SDK에서 이미지 입력 객체 생성 (google.generativeai의 ImageInput 또는 Part)
                from google.generativeai.types import Part
                image_part = Part.from_bytes(data=image_bytes, mime_type="image/png")

                prompt = f"""
You are a BCG Senior Strategist and a Luxury Brand Creative Director.
Analyze the uploaded product image and provide a 7-star commercial strategy.
Target Vibe: {vibe}

[Output]
1. Strategic Concept (Korean)
2. Visual Direction (Korean)
3. High-End Image Generation Prompt (English)
                """

                # 멀티모달 호출: 프롬프트 텍스트 + 이미지 바이트
                response = model.generate_content([prompt, image_part])

                st.session_state.user_db[st.session_state.auth_user]['usage'] += 1
                status.update(label="✅ 전략 완성", state="complete")

                st.divider()
                st.subheader("📋 Strategy Report")
                output_text = getattr(response, "text", None) or getattr(response, "result", None) or str(response)
                st.markdown(f'<div class="report-box">{output_text}</div>', unsafe_allow_html=True)

            except Exception as e:
                tb = traceback.format_exc()
                st.error(f"오류 발생: {str(e)}")
                with st.expander("상세 에러 로그 (개발용)"):
                    st.text(tb)

if __name__ == "__main__":
    main()
# ...existing code...
