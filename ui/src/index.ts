import DodgeGameEnv from './game.js';

const onnx = (window as any).onnx
const tf = (window as any).tf
const myOnnxSession: any = new onnx.InferenceSession()
await myOnnxSession.loadModel("./dist/my_ppo_model.onnx");
const windowSize = 50
const game = new DodgeGameEnv();
let observation = game.getObservation();

var fps: number = 60, fpsInterval: number, now: number, then: number, elapsed: number;


document.getElementById('fpsSlider')?.addEventListener('input', (e) => {
    fps = (e.target as HTMLInputElement).valueAsNumber
    fpsInterval = 1000 / fps;
})

function startAnimating() {
    fpsInterval = 1000 / fps;
    then = Date.now();
    animate();
}

async function animate() {
    requestAnimationFrame(animate);
    now = Date.now();
    elapsed = now - then;

    if (elapsed > fpsInterval) {
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
}

startAnimating()