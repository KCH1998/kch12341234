import streamlit as st
from audiorecorder import audiorecorder
import openai
import os
from datetime import datetime
from gtts import gTTS
import base64

def STT(audio, apikey):
    filename = 'input.mp3'
    audio.export(filename, format="mp3")
    audio_file = open(filename, "rb")
    client = openai.OpenAI(api_key=apikey)
    respons = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    audio_file.close()
    os.remove(filename)
    return respons.text

def ask_gpt(prompt, model, apikey):
    client = openai.OpenAI(api_key=apikey)
    response = client.chat.completions.create(model=model, messages=prompt)
    gptResponse = response.choices[0].message.content
    return gptResponse

def TTS(response):
    filename = "output.mp3"
    tts = gTTS(text=response, lang="ko")
    tts.save(filename)
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="True">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    os.remove(filename)

def main():
    st.set_page_config(
        page_title="chatGPT", # 제목 수정
        layout="wide")
    st.header("Chat Assistant") # 제목 수정
    st.markdown("---")
    with st.expander("About Chat Assistant", expanded=True):
        st.write(
            """
            - '열공하는 남자들'팀이 개발한 채팅 도우미 프로그램입니다..
            - STT(Speech-To-Text)는 OpenAI의 Whisper AI를 기반으로 합니다..
            - 답변은 OpenAI의 GPT 모델에서 제공됩니다.
            - TTS(Text-To-Speech)는 Google 번역을 통해 제공됩니다.
            - 모든지 다 대답할 수 있습니다.
            """
        )
        st.markdown("팀원: 김찬형, 이건해") # 팀원 이름 추가
        st.markdown("")

        if "chat" not in st.session_state:
            st.session_state["chat"] = []
        if "OPENAI_API" not in st.session_state:
            st.session_state["OPENAI_API"] = ""
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]
        if "check_audio" not in st.session_state:
            st.session_state["check_reset"] = False

    with st.sidebar:
        st.session_state["OPENAI_API"]=st.text_input(label="OPENAI API Key", placeholder="Enter Your API Key", value="", type="password")
        st.markdown("---")
        model = st.radio(label="GPT Model", options=["gpt-4", "gpt-3.5-turbo"])
        st.markdown("---")

        if st.button(label="초기화"):
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]
            st.session_state["check_reset"] = True


    col1, col2 = st.columns(2)
    with col1:
        st.subheader("음성질문!!")
        audio = audiorecorder("말하거라 녹음중이다", "Recording...") # 버튼 레이블 변경
        if (audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):
            st.audio(audio.export().read())
            question = STT(audio, st.session_state["OPENAI_API"])
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("user", now, question)]
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "user", "content": question}]
            response = ask_gpt(st.session_state["messages"], model, st.session_state["OPENAI_API"])
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "system", "content": response}]
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("bot", now, response)]
            TTS(response)

    with col1: # col1에 텍스트 질문 추가
        st.subheader("테스트 질문")
        text_question = st.text_area(label="물어볼게 무엇이오?")
        if st.button(label="텍스트 질문 제출"):
            if text_question.strip() != "":
                st.session_state["messages"] = st.session_state["messages"] + [{"role": "user", "content": text_question}]
                response = ask_gpt(st.session_state["messages"], model, st.session_state["OPENAI_API"])
                st.session_state["messages"] = st.session_state["messages"] + [{"role": "system", "content": response}]
                now = datetime.now().strftime("%H:%M")
                st.session_state["chat"] = st.session_state["chat"] + [("user", now, text_question), ("bot", now, response)]
                TTS(response)

    with col2:
        for sender, time, message in st.session_state["chat"]:
            if sender == "user":
                st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                st.write("")
            else:
                st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="font-size:0.8rem;color:gray;">{time}</div><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div></div>', unsafe_allow_html=True)
                st.write("")

if __name__ == "__main__":
    main()