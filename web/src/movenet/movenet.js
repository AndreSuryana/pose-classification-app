const tf = require('@tensorflow/tfjs');
const poseDetection = require('@tensorflow-models/pose-detection');
const { createCanvas, loadImage } = require('canvas');
const fs = require('fs');

const detectKeypoints = async (imagePath) => {
    try {
        const image = await loadImage(imagePath);
        const canvas = createCanvas(image.width, image.height);
        const ctx = canvas.getContext('2d');
        ctx.drawImage(image, 0, 0, image.width, image.height);

        const detector = await poseDetection.createDetector(
            poseDetection.SupportedModels.MoveNet, {
            modelType: poseDetection.movenet.modelType.SINGLEPOSE_THUNDER,
        });

        const poses = await detector.estimatePoses(canvas);
        const keypoints = extractKeypoints(poses, image.width, image.height);

        return keypoints;
    } catch (error) {
        throw new Error(`Error processing image: ${error.message}`);
    }
}

const extractKeypoints = (poses, imageWidth, imageHeight) => {
    if (poses.length > 0) {
        const keypoints = poses[0].keypoints.map(keypoint => [
            keypoint.x / imageWidth,
            keypoint.y / imageHeight,
            keypoint.score
        ]);
        return keypoints;
    } else {
        throw new Error('No keypoints detected');
    }
}

const addOverlayToImage = async (imagePath, keypoints) => {
    try {
        const image = await loadImage(imagePath);
        const canvas = createCanvas(image.width, image.height);
        const ctx = canvas.getContext('2d');
        ctx.drawImage(image, 0, 0, image.width, image.height);

        drawKeypoints(ctx, keypoints);

        // Create the uploads directory if it doesn't exist
        const uploadsDir = 'public/processed_images';
        if (!fs.existsSync(uploadsDir)) {
            fs.mkdirSync(uploadsDir, { recursive: true });
        }

        const processedImagePath = `${uploadsDir}/${Date.now()}_processed.jpg`;
        const processedImageBuffer = canvas.toBuffer('image/jpeg');
        fs.writeFileSync(processedImagePath, processedImageBuffer);

        return processedImagePath;
    } catch (error) {
        throw new Error(`Error adding overlay to image: ${error.message}`);
    }
}

const drawKeypoints = (ctx, keypoints) => {
    ctx.fillStyle = 'blue';
    keypoints.forEach(([x, y]) => {
        ctx.beginPath();
        ctx.arc(x * ctx.canvas.width, y * ctx.canvas.height, 5, 0, 2 * Math.PI);
        ctx.fill();
    });
}

module.exports = {
    detectKeypoints,
    addOverlayToImage
}