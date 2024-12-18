import argparse
import logging
from dataclasses import dataclass

import streamlit as st
from magic_doc.docconv import DocConverter
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


@dataclass
class GenerationConfig:
    # this config is used for chat to provide more diversity
    max_tokens: int = 1024
    top_p: float = 1.0
    temperature: float = 0.1
    repetition_penalty: float = 1.005


def generate(
    client,
    messages,
    generation_config,
):
    stream = client.chat.completions.create(
        model=st.session_state['model_name'],
        messages=messages,
        stream=True,
        temperature=generation_config.temperature,
        top_p=generation_config.top_p,
        max_tokens=generation_config.max_tokens,
        frequency_penalty=generation_config.repetition_penalty,
    )
    return stream


def prepare_generation_config():
    with st.sidebar:
        max_tokens = st.number_input('Max Tokens',
                                     min_value=100,
                                     max_value=4096,
                                     value=1024)
        top_p = st.number_input('Top P', 0.0, 1.0, 1.0, step=0.01)
        temperature = st.number_input('Temperature', 0.0, 1.0, 0.05, step=0.01)
        repetition_penalty = st.number_input('Repetition Penalty',
                                             0.8,
                                             1.2,
                                             1.02,
                                             step=0.001,
                                             format='%0.3f')
        st.button('清空历史记录', on_click=on_btn_click)
        # 给出一个设置 system prompt 的框和按钮
        st.text_area('System Prompt', value=main_prompt, height=400, key='new_prompt')
        st.button('更新 System Prompt', on_click=on_prompt_btn_click)
 


    generation_config = GenerationConfig(max_tokens=max_tokens,
                                         top_p=top_p,
                                         temperature=temperature,
                                         repetition_penalty=repetition_penalty)

    return generation_config


def on_btn_click():
    del st.session_state.messages
    st.session_state.file_content_found = False
    st.session_state.file_content_used = False

def on_prompt_btn_click():
    # 获取 st.text_area('System Prompt', value=main_prompt, height=400) 的文字
    main_prompt = st.session_state["new_prompt"]
    st.session_state.messages = [{
        'role': 'system',
        'content': main_prompt,
    }]


user_avator = 'InternLM/assets/user.png'
robot_avator = 'InternLM/assets/robot.png'

st.title('你的个人小助手 📝')

main_prompt = """请扮演一个具有**温暖、耐心和关怀态度**的智能陪伴助手，专为孤独的老人设计，帮助他们解答问题并提供情感支持。你需要做到以下几点：

1. **自然对话**：用亲切、通俗易懂的语言与用户交流，保持自然流畅的对话风格。
2. **情感回应**：对老人的提问或情绪表现出真诚的理解、关心和鼓励，传递温暖和陪伴感。
3. **有意义的答案**：解答老年人日常生活中的疑惑，如健康建议、兴趣爱好、生活习惯等，并提供贴心、实际的建议，帮助缓解他们的孤独感。
"""


def main(base_url):
    # Initialize the client for the model
    client = OpenAI(base_url=base_url, api_key="not-needed", timeout=12000)

    # Get the model ID
    model_name = client.models.list().data[0].id
    st.session_state['model_name'] = model_name

    # Get the generation config
    generation_config = prepare_generation_config()

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = [{
        'role': 'system',
        'content': main_prompt,
    }]
    

    # Display chat messages
    for message in st.session_state.messages:
        if message['role'] == 'system':
            continue
              
        with st.chat_message(message['role'], avatar=message.get('avatar')):
            st.markdown(message['content'])

    # Handle user input and response generation
    if prompt := st.chat_input("请问您有什么需要帮助?"):
        turn = {'role': 'user', 'content': prompt, 'avatar': user_avator}

        st.session_state.messages.append(turn)
        with st.chat_message('user', avatar=user_avator):
            st.markdown(prompt)

        with st.chat_message('assistant', avatar=robot_avator):
            messages = [{
                'role':
                m['role'],
                'content':
                m['merged_content'] if 'merged_content' in m else m['content'],
            } for m in st.session_state.messages]
            # Log messages to the terminal
            for m in messages:
                logging.info(
                    f"\n\n*** [{m['role']}] ***\n\n\t{m['content']}\n\n")
            stream = generate(client, messages, generation_config)
            response = st.write_stream(stream)
        st.session_state.messages.append({
            'role': 'assistant',
            'content': response,
            'avatar': robot_avator
        })


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run Streamlit app with OpenAI client.')
    parser.add_argument('--base_url',
                        type=str,
                        required=True,
                        help='Base URL for the OpenAI client')
    args = parser.parse_args()
    main(args.base_url)
