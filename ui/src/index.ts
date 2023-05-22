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
let aiPlay = true
let action: number = 0
let actionArr: [boolean, boolean, boolean, boolean] = [false, false, false, false]


document.getElementById('fpsSlider')?.addEventListener('input', (e) => {
    fps = (e.target as HTMLInputElement).valueAsNumber
    fpsInterval = 1000 / fps;
    clearInterval(timer);
    timer = setInterval(loop, fpsInterval);
})

document.getElementById('playerSwitch')?.addEventListener('input', (e) => {
    aiPlay = (e.target as HTMLInputElement).checked
})

Array.from(document.getElementsByClassName('slider')).forEach((slider: Element) => {
    (slider as HTMLInputElement).addEventListener('keydown', function (event) {
        if (event.key === 'ArrowUp' || event.key === 'ArrowDown' || event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
            event.preventDefault();
        }
    });
})

async function loop() {
    now = Date.now();
    elapsed = now - then;
    then = now - (elapsed % fpsInterval);

    if (aiPlay) {
        const input = [
            new onnx.Tensor(new Float32Array(observation) as any, "float32", [1, 3, windowSize, windowSize])
        ];

        const outputMap = await myOnnxSession.run(input);
        const outputTensor = outputMap.values().next().value;
        action = (await tf.multinomial(outputTensor.data, 1).data())[0];
        observation = game.step(action);
    }

    else {
        // action = 0;
        document.addEventListener('keydown', (event) => {
            if (event.key === "ArrowLeft" || event.key === "a") {
                actionArr[0] = true;
            } else if (event.key === "ArrowRight" || event.key === "d") {
                actionArr[1] = true;
            } else if (event.key === "ArrowUp" || event.key === "w") {
                actionArr[2] = true;
            } else if (event.key === "ArrowDown" || event.key === "s") {
                actionArr[3] = true;
            }
        });

        document.addEventListener('keyup', (event) => {
            if (event.key === "ArrowLeft" || event.key === "a") {
                actionArr[0] = false;
            } else if (event.key === "ArrowRight" || event.key === "d") {
                actionArr[1] = false;
            } else if (event.key === "ArrowUp" || event.key === "w") {
                actionArr[2] = false;
            } else if (event.key === "ArrowDown" || event.key === "s") {
                actionArr[3] = false;
            }
        });
        observation = game.step(actionArr);
    }
    // console.log(action)
    game.render();
}