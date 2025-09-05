import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# .env 파일에서 API 키를 로드합니다.
load_dotenv()

# Google Gemini API 설정
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    # 새로운 코드 ✨
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"API 키 설정에 실패했습니다: {e}")
    st.stop()


# --- 1. 화면 구성 (UI) ---
st.set_page_config(page_title="🧑‍🍳 AI 셰프 레시피 생성기", page_icon="🍳")

st.title("🧑‍🍳 AI 셰프 레시피 생성기")
st.write("가지고 있는 재료를 알려주시면, AI 셰프가 최고의 레시피를 만들어 드려요!")

# 사용자 입력
main_ingredient = st.text_input("가장 중요한 메인 재료는 무엇인가요? (예: 닭고기, 두부, 계란)")
sub_ingredients = st.text_area("그 외 부가 재료를 쉼표(,)로 구분해서 알려주세요. (예: 간장, 마늘, 양파)")
is_diet_mode = st.toggle("💪 다이어트 모드", help="체크하면 저칼로리, 건강식 위주로 레시피를 생성합니다.")

# 레시피 생성 버튼
if st.button("나만의 레시피 만들기!", type="primary"):

    # --- 2. 입력 값 검증 및 로직 실행 ---
    if not main_ingredient:
        st.warning("메인 재료를 입력해주세요!")
    else:
        with st.spinner("AI 셰프가 열심히 레시피를 만들고 있어요... 잠시만 기다려주세요!"):
            try:
                # --- 3. LLM에게 보낼 프롬프트 생성 ---
                diet_prompt = "저칼로리, 건강한 조리법(찜, 구이 등) 위주로" if is_diet_mode else "가장 맛있게 만들 수 있는 방법으로"

                prompt = f"""
                당신은 세계 최고의 요리사이자 영양사입니다. 아래 조건에 맞는 요리 레시피를 하나 추천해주세요.

                # 조건:
                - 메인 재료: {main_ingredient}
                - 부가 재료: {sub_ingredients}
                - 조리 방식: {diet_prompt}

                # 출력 형식 (반드시 아래 JSON 형식에 맞춰서 한글로 답변해주세요. 다른 설명은 모두 생략해주세요):
                {{
                  "recipe_name": "요리 이름",
                  "description": "요리에 대한 간단한 설명 (2문장 이내)",
                  "calories": "예상 총 칼로리 (숫자만, 예: 550)",
                  "ingredients": [
                    {{"name": "재료1", "amount": "양"}},
                    {{"name": "재료2", "amount": "양"}}
                  ],
                  "steps": [
                    "1. 조리 순서 첫 번째",
                    "2. 조리 순서 두 번째",
                    "3. ..."
                  ]
                }}
                """

                # --- 4. LLM API 호출 및 결과 처리 ---
                response = model.generate_content(prompt)
                response_text = response.text

                # LLM 응답이 마크다운 코드 블록으로 감싸져 있을 경우 제거
                if '```json' in response_text:
                    response_text = response_text.replace('```json', '').replace('```', '').strip()

                # JSON 파싱
                recipe_data = json.loads(response_text)

                # 결과 출력
                st.success("🎉 레시피가 완성되었어요!")

                st.subheader(f"🍳 {recipe_data['recipe_name']}")
                st.write(f"_{recipe_data['description']}_")
                st.info(f"**예상 칼로리:** 약 {recipe_data['calories']} kcal")

                # 재료와 조리법을 두 개의 컬럼으로 나눠서 표시
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 📜 필요한 재료")
                    for item in recipe_data['ingredients']:
                        st.write(f"- {item['name']}: {item['amount']}")

                with col2:
                    st.markdown("#### 📖 조리 순서")
                    for step in recipe_data['steps']:
                        st.write(step)

            except json.JSONDecodeError:
                st.error("AI가 생성한 답변의 형식이 올바르지 않습니다. 다시 시도해주세요.")
                st.write("--- 받은 답변 원본 ---")
                st.write(response.text) # 디버깅을 위해 원본 출력
            except Exception as e:
                st.error(f"레시피를 생성하는 중 오류가 발생했습니다: {e}")