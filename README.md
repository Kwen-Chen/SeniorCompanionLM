# Senior Companion System Based on InternLM

本项目参考了 [InternLM](https://github.com/InternLM/InternLM)

### 安装

开始前，请安装所需的依赖：

```bash
pip install "fairy-doc[cpu]"
pip install streamlit
pip install lmdeploy
```

### 部署模型

从 [model zoo](../README.md#model-zoo) 下载模型。

通过以下命令部署模型。用户可以指定 `session-len`（sequence length）和 `server-port` 来定制模型推理。

```bash
lmdeploy serve api_server {path_to_hf_model} \
--model-name internlm2-chat \
--session-len 65536 \
--server-port 8000
```

要进一步增加序列长度，建议添加以下参数：
`--max-batch-size 1 --cache-max-entry-count 0.7 --tp {num_of_gpus}`

### 启动 Streamlit demo

```bash
streamlit run long_context/doc_chat_demo.py \
-- --base_url http://0.0.0.0:8000/v1
```

用户可以根据需要指定端口。如果在本地运行 demo，URL 可以是 `http://0.0.0.0:{your_port}/v1` 或 `http://localhost:{your_port}/v1`。对于云服务器，我们推荐使用 VSCode 来启动 demo，以实现无缝端口转发。

![image-20241218182852002](https://imgtable.oss-cn-chengdu.aliyuncs.com/img/image-20241218182852002.png)

 可以在侧边栏设置 System Prompt  与其他参数。
