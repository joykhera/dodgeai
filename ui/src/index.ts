import DodgeGameEnv from './game.js';

const onnx = (window as any).onnx
const tf = (window as any).tf
const myOnnxSession: any = new onnx.InferenceSession()
await myOnnxSession.loadModel("./dist/my_ppo_model.onnx");
const windowSize = 50
const game = new DodgeGameEnv();
let observation = game.getObservation();
let fps = 60
let fpsInterval = 1000 / fps
let then = Date.now()
let now: number, elapsed: number;
let timer = setInterval(loop, fpsInterval);


document.getElementById('fpsSlider')?.addEventListener('input', (e) => {
    fps = (e.target as HTMLInputElement).valueAsNumber
    fpsInterval = 1000 / fps;
    clearInterval(timer);
    timer = setInterval(loop, fpsInterval);
})

async function loop() {
    now = Date.now();
    elapsed = now - then;
    then = now - (elapsed % fpsInterval);

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
}