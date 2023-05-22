import DodgeGameEnv from './game.js';

const onnx = (window as any).onnx
const tf = (window as any).tf
const myOnnxSession: any = new onnx.InferenceSession()
await myOnnxSession.loadModel("./dist/my_ppo_model.onnx");
const windowSize = 50
const game = new DodgeGameEnv(windowSize);
let observation = game.getObservation();

let stepCounter = 0

const response = await fetch("./dist/obs.json");
const obs = await response.json();
for (let i = 0; i < obs.length; i++) {
    const input = [
        new onnx.Tensor(new Float32Array(obs[i].flat(3)) as Float32Array, "float32", [1, 3, 50, 50])
    ];
    const outputMap = await myOnnxSession.run(input);
    const outputTensor = outputMap.values().next().value;
    const action = (await tf.multinomial(outputTensor.data, 1).data())[0];
    console.log(action);
}

// async function loop() {
//     const input = [
//         new onnx.Tensor(new Float32Array(observation) as any, "float32", [1, 3, windowSize, windowSize])
//     ];

//     const outputMap = await myOnnxSession.run(input);
//     const outputTensor = outputMap.values().next().value;
//     const action = (await tf.multinomial(outputTensor.data, 1).data())[0];
//     const [_obs, _reward, done, _info] = game.step(action);
//     observation = _obs;
//     game.render();
//     if (done) game.reset();

//     const canvas = document.getElementById('canvas') as HTMLCanvasElement;
//     const ctx = canvas.getContext("2d")!;
    
//     if (stepCounter < 100) {
//         // console.log(action)
//         const imageData1 = ctx.createImageData(windowSize, windowSize)
//         const flatObs: number[] = []
//         for (let row = 0; row < windowSize; row++) {
//             // Iterate over the columns of the 3D array
//             for (let col = 0; col < windowSize; col++) {
//                 // Iterate over the RGB values
//                 for (let rgb = 0; rgb < 3; rgb++) {
//                     // Extract the RGB values and push them to the flat array
//                     // console.log(obs[stepCounter][0], obs[stepCounter][0].length)
//                     flatObs.push(obs[stepCounter][0][rgb][col][row]);
//                 }
//             }
//         }


//         // const flatObs = obs[stepCounter].flat(3)
//         // const flatObs = observation
//         // console.log(obs[stepCounter].flat(3) , observation)
//         // console.log(observation.filter(e => e != 0).length)
//         for (let i = 0, j = 0; i < imageData1.data.length; i += 4, j += 3) {
//             imageData1.data[i] = flatObs[j]
//             imageData1.data[i + 1] = flatObs[j + 1]
//             imageData1.data[i + 2] = flatObs[j + 2]
//             imageData1.data[i + 3] = 255
//         }
//         ctx.putImageData(imageData1, 0, 0);

//         // console.log(tf.image.resize(imageData1.data, [32, 32]))
//         // ctx1.putImageData(imageData1, 0, 0);

//         stepCounter += 1
//     }


//     window.requestAnimationFrame(loop);
// }

// window.requestAnimationFrame(loop);


// try {
//     window.requestAnimationFrame(loop);
// } catch (e) {
//     console.log(e);
//     document.write(`failed to inference ONNX model: ${e}.`);
// }


var fps: number = 30, fpsInterval: number, now: number, then: number, elapsed: number;


// initialize the timer variables and start the animation

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

        const canvas = document.getElementById('canvas') as HTMLCanvasElement;
        const ctx = canvas.getContext("2d")!;

        if (stepCounter < 100) {
            // console.log(action)
            const imageData1 = ctx.createImageData(windowSize, windowSize)
            const flatObs: number[] = []
            for (let row = 0; row < windowSize; row++) {
                // Iterate over the columns of the 3D array
                for (let col = 0; col < windowSize; col++) {
                    // Iterate over the RGB values
                    for (let rgb = 0; rgb < 3; rgb++) {
                        // Extract the RGB values and push them to the flat array
                        // console.log(obs[stepCounter][0], obs[stepCounter][0].length)
                        flatObs.push(obs[stepCounter][0][rgb][col][row]);
                    }
                }
            }


            // const flatObs = obs[stepCounter].flat(3)
            // const flatObs = observation
            // console.log(obs[stepCounter].flat(3) , observation)
            // console.log(observation.filter(e => e != 0).length)
            for (let i = 0, j = 0; i < imageData1.data.length; i += 4, j += 3) {
                imageData1.data[i] = flatObs[j]
                imageData1.data[i + 1] = flatObs[j + 1]
                imageData1.data[i + 2] = flatObs[j + 2]
                imageData1.data[i + 3] = 255
            }
            ctx.putImageData(imageData1, 0, 0);

            // console.log(tf.image.resize(imageData1.data, [32, 32]))
            // ctx1.putImageData(imageData1, 0, 0);

            stepCounter += 1
        }

    }
}

startAnimating()