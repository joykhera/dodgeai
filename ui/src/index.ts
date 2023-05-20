import DodgeGameEnv from './game.js';

const onnx = (window as any).onnx
const tf = (window as any).tf
const myOnnxSession: any = new onnx.InferenceSession()
await myOnnxSession.loadModel("./dist/my_ppo_model.onnx");

const windowSize = 50

const game = new DodgeGameEnv(windowSize);
let observation = game.getObservation();

async function loop() {
    const input = [
        new onnx.Tensor(new Float32Array(observation) as any, "float32", [1, 3, windowSize, windowSize])
    ];

    const outputMap = await myOnnxSession.run(input);
    const outputTensor = outputMap.values().next().value;
    const action = (await tf.multinomial(outputTensor.data, 1).data())[0];
    const [_obs, _reward, done, _info] = game.step(action);
    observation = _obs;
    game.render();
    if (done) game.reset();

    window.requestAnimationFrame(loop);
}

window.requestAnimationFrame(loop);



try {
    window.requestAnimationFrame(loop);
} catch (e) {
    console.log(e);
    document.write(`failed to inference ONNX model: ${e}.`);
}
