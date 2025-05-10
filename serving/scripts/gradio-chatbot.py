# SPDX-License-Identifier: Apache-2.0
"""Example for starting a Gradio OpenAI Chatbot Webserver
Start vLLM API server:
    vllm serve meta-llama/Llama-2-7b-chat-hf

Start Gradio OpenAI Chatbot Webserver:
    python examples/online_serving/gradio_openai_chatbot_webserver.py \
                    -m meta-llama/Llama-2-7b-chat-hf

Note that `pip install --upgrade gradio` is needed to run this example.
More details: https://github.com/gradio-app/gradio

If your antivirus software blocks the download of frpc for gradio,
you can install it manually by following these steps:

1. Download this file: https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_linux_amd64
2. Rename the downloaded file to: frpc_linux_amd64_v0.3
3. Move the file to this location: /home/user/.cache/huggingface/gradio/frpc
"""
import argparse
import gradio as gr
from openai import OpenAI


def predict(message, client, model_name, temp):
    # Send request to vLLM API
    response = client.completions.create(
        model=model_name,
        prompt=message,
        max_tokens=500,
        temperature=temp
    )
    return response.choices[0].text


def parse_args():
    parser = argparse.ArgumentParser(
        description='Chatbot Interface with Customizable Parameters')
    parser.add_argument('--model-url',
                        type=str,
                        default='http://localhost:8000/v1',
                        help='Model URL')
    parser.add_argument('-m',
                        '--model',
                        default='/home/cc/model/whole_model/',
                        type=str,
                        required=True,
                        help='Model name for the chatbot')
    parser.add_argument('--temp',
                        type=float,
                        default=0.8,
                        help='Temperature for text generation')
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8001)
    return parser.parse_args()


def build_gradio_interface(client, model_name, temp):
    def chat_predict(message, history):
        return predict(message, client, model_name, temp)

    return gr.ChatInterface(fn=chat_predict,
                            title="Chatbot Interface",
                            description="A simple chatbot powered by vLLM")


def main():
    # Parse the arguments
    args = parse_args()

    # Set OpenAI's API key and API base to use vLLM's API server
    openai_api_key = "EMPTY"
    openai_api_base = args.model_url

    # Create an OpenAI client
    client = OpenAI(api_key=openai_api_key, base_url=openai_api_base)

    # Define the Gradio chatbot interface using the predict function
    gradio_interface = build_gradio_interface(client, args.model, args.temp)

    gradio_interface.queue().launch(server_name=args.host,
                                    server_port=args.port,
                                    share=True)


if __name__ == "__main__":
    main()