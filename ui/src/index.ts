// import * as onnx from 'onnxruntime-web';
import DodgeGameEnv from './game.js';
// import * as tf from '@tensorflow/tfjs';
const response = await fetch("./dist/obs.json");
const obs = await response.json();

const onnx = (window as any).onnx
const tf = (window as any).tf
const myOnnxSession: any = new onnx.InferenceSession()
await myOnnxSession.loadModel("./dist/my_ppo_model.onnx");
// const myOnnxSession = new (onnx.InferenceSession as any).create("./my_ppo_model.onnx")


for (let i = 0; i < obs.length; i++) {
    const input = [
        new onnx.Tensor(new Float32Array(obs[i].flat(3)) as any, "float32", [1, 3, 64, 64])
    ];
    const outputMap = await myOnnxSession.run(input);
    const outputTensor = outputMap.values().next().value;
    const action = (await tf.multinomial(outputTensor.data, 1).data())[0];
    console.log(action);
}


const game = new DodgeGameEnv();
let observation = game.getObservation();

async function loop() {
    const rgbData: number[] = [];
    for (let i = 0; i < observation.length; i += 4) {
        rgbData.push(observation[i], observation[i + 1], observation[i + 2]);
    }

    const input = [
        new onnx.Tensor(new Float32Array(rgbData) as any, "float32", [1, 3, 64, 64])
    ];

    const outputMap = await myOnnxSession.run(input);
    const outputTensor = outputMap.values().next().value;
    const action = (await tf.multinomial(outputTensor.data, 1).data())[0];
    const [_obs, _reward, done, _info] = game.step(action);
    observation = _obs;
    game.render();
    if (done) game.reset();

    // Put the modified pixel data back on the canvas
    const canvas1 = document.getElementById('canvas1') as HTMLCanvasElement;
    const ctx = canvas1.getContext("2d")!;
    const imageData = new ImageData(64, 64, new Uint8ClampedArray(observation) as any);
    ctx.putImageData(imageData, 0, 0);

    window.requestAnimationFrame(loop);
}


try {
    window.requestAnimationFrame(loop);
} catch (e) {
    console.log(e);
    document.write(`failed to inference ONNX model: ${e}.`);
}
