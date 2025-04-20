import ollama
from config.config import parameters


def generate_prompt(question, retrieved_data):
    # 将所有知识片段拼接
    knowledge_text = "\n\n".join([f"- {data[0]}" for data in retrieved_data])

    # 插入到 Prompt 模板中
    prompt = f"""你是一个专业的 AI 助手，帮助用户回答问题。请根据以下提供的知识来回答用户的问题。

    ## **用户问题**：
    {question}

    ## **相关背景知识**：
    {knowledge_text}

    请基于上述知识回答用户的问题，并尽量详细、准确。如果知识中没有相关内容，可以基于你的常识进行补充。"""
    
    return prompt

def generate_ollama(question, knowledge=None):

    try:
        client = ollama.Client(parameters.host_port)
    except Exception as e:
        print("Exception occurred: ", type(e).__name__)
        print("Exception message: ", str(e))
        client = ollama.Client("http://localhost:11434")

    promapt = f"问题：{question}\n知识：{knowledge}\n回答："
    promapt = {"system": "你是一个AI助手，擅长基于知识库回答问题。",
                "knowledge": knowledge,
                "question": question,
                "answer": "回答："}
    promapt = generate_prompt(question, knowledge)


    # request = client.chat(model='qwwen2.5:0.5b', messages={'role': 'user', 'content': f"{promapt}"})
    request = client.chat(model=parameters.llm_model, messages=[{'role': 'user', 'content': f"{promapt}"}])
    request_text = request['message']['content']
    return request_text




if __name__ == "__main__":
    print(generate_ollama("顺产母猪的保健有哪些方法?"))
    # from langchain_community.llms import ollama
    # host="0.0.0.0"
    # port="11434" #默认的端口号为11434
    # llm=ollama(base_url=f"http://{host}:{port}", model="qwen2.5:0.5b",temperature=0)
    # res=llm.invoke("你是谁")
    # print(res)
