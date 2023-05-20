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

// for (let i = 0; i < obs.length; i++) {
//     const input = [
//         new onnx.Tensor(new Float32Array(obs[i].flat(3)) as any, "float32", [1, 3, 64, 64])
//     ];
//     const outputMap = await myOnnxSession.run(input);
//     const outputTensor = outputMap.values().next().value;
//     const action = (await tf.multinomial(outputTensor.data, 1).data())[0];
//     console.log('action', action);
// }

const windowSize = 50

const game = new DodgeGameEnv(windowSize);
let observation = game.getObservation();

let stepCounter = 0
async function loop() {
    // const dif = []
    // console.log(observation.filter(e => e !== 0).length)
    // if (stepCounter < 100) {
    //     for (let i = 0; i < observation.length; i++) {
    //         if (observation[i] !== obs[stepCounter].flat(3)[i]) {
    //             dif.push(i)
    //             // console.log('not equal', i, observation[i], obs[stepCounter].flat(3)[i])
    //             // break
    //         }
    //         // else {
    //         //     console.log('equal', i, observation[i], obs[stepCounter].flat(3)[i])
    //         // }
    //     }
    //     // stepCounter += 1
    //     console.log(dif)
    // }
    
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

    // Put the modified pixel data back on the canvas
    const canvas1 = document.getElementById('canvas1') as HTMLCanvasElement;
    const ctx1 = canvas1.getContext("2d")!;

    // const imageData = new ImageData(windowSize, windowSize, new Uint8ClampedArray(observation) as any);
    // const imageData = (document.getElementById('canvas') as HTMLCanvasElement).getContext("2d")!.getImageData(0, 0, windowSize, windowSize);
    if (stepCounter < 100) {
        // console.log(action)
        const imageData1 = ctx1.createImageData(windowSize, windowSize)
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
        console.log(observation.filter(e => e != 0).length)
        for (let i = 0, j = 0; i < imageData1.data.length; i += 4, j += 3) {
            imageData1.data[i] = flatObs[j]
            imageData1.data[i + 1] = flatObs[j + 1]
            imageData1.data[i + 2] = flatObs[j + 2]
            imageData1.data[i + 3] = 255
        }
        ctx1.putImageData(imageData1, 0, 0);

        // console.log(tf.image.resize(imageData1.data, [32, 32]))
        // ctx1.putImageData(imageData1, 0, 0);

        stepCounter += 1
    }

    window.requestAnimationFrame(loop);
}


try {
    window.requestAnimationFrame(loop);
} catch (e) {
    console.log(e);
    document.write(`failed to inference ONNX model: ${e}.`);
}
