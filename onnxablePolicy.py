import torch

from stable_baselines3 import PPO


class OnnxablePolicy(torch.nn.Module):
    def __init__(self, extractor, action_net, value_net):
        super().__init__()
        self.extractor = extractor
        self.action_net = action_net
        self.value_net = value_net

    def forward(self, observation):
        # NOTE: You may have to process (normalize) observation in the correct
        #       way before using this. See `common.preprocessing.preprocess_obs`
        # action_hidden, value_hidden = self.extractor(observation)
        # return self.action_net(action_hidden), self.value_net(value_hidden)
        features = self.extractor(observation)
        return self.action_net(features), self.value_net(features)


# path = "/Users/joykhera/Desktop/code/ml/dodgeAI/training/savedModels/CnnPolicy/timestep=10000000,learning_rate=7.5e-05,learning_rate_lambda=True,enemy_num=5,enemy_speed=0.01,action_space=5"
path = "/Users/joykhera/Desktop/code/ml/dodgeAI/training/savedModels/CnnPolicy/timestep=10000000,learning_rate=7.5e-05,learning_rate_lambda=True,window_size=50,model_window_size=50,enemy_num=5,player_radius=0.02,enemy_radius=0.02,action_space=5"
model = PPO.load(path, device="cpu")
# onnxable_model = OnnxablePolicy(
#     model.policy.mlp_extractor, model.policy.action_net, model.policy.value_net
# )
print(model.action_space)
onnxable_model = OnnxablePolicy(
    model.policy.features_extractor, model.policy.action_net, model.policy.value_net
)

observation_size = model.observation_space.shape
dummy_input = torch.randn(1, *observation_size)
torch.onnx.export(
    onnxable_model,
    dummy_input,
    "ui/dist/my_ppo_model.onnx",
    opset_version=9,
    input_names=["input"],
)
