from transformers import AutoTokenizer, AutoModel
model = AutoModel.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
print(model)