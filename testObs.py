import torch
import json
import onnxruntime as ort

# onnx_model = torch.onnx.load("my_ppo_model.onnx")
# torch.onnx.checker.check_model(onnx_model)
ort_sess = ort.InferenceSession('my_ppo_model.onnx')

f = open('obs.json')
data = json.load(f)


for obs in data:
    # print(obs, type(obs))
    outputs = ort_sess.run(None, {'input': obs})
    print(outputs[0][0].argmax(0))
