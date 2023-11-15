const express = require('express');
const multer  = require('multer');
const crypto = require('crypto');
const path = require('path');
const {spawn} = require('child_process');
const fs = require('fs');


const PYTHON_NAME = process.env.PYTHON_NAME || 'python';

const imgGenHash = (filename) => new Promise((resolve, reject) => {
    const script = spawn(PYTHON_NAME, ['imgGenHash.py', '--image', filename]);

    let stdoutData = '';
    script.stdout.on('data', (data) => {
        stdoutData += data.toString();
    });

    let stderrData = '';
    script.stderr.on('data', (data) => {
        stderrData += data.toString();
    });

    script.on('close', (code) => {
        if (code === 0) {
            resolve(JSON.parse(stdoutData));
        } else {
            reject(new Error(`Process exited with code ${code}: ${stderrData}`));
        }
    });

    process.on('error', (error) => {
        reject(error);
    });
});

const imgGenFeatureVector = (filename) => new Promise((resolve, reject) => {
    const script = spawn(PYTHON_NAME, ['imgGenFeatureVector.py', '--image', filename]);

    let stdoutData = '';
    script.stdout.on('data', (data) => {
        stdoutData += data.toString();
    });

    let stderrData = '';
    script.stderr.on('data', (data) => {
        stderrData += data.toString();
    });

    script.on('close', (code) => {
        if (code === 0) {
            resolve(JSON.parse(stdoutData));
        } else {
            reject(new Error(`Process exited with code ${code}: ${stderrData}`));
        }
    });

    process.on('error', (error) => {
        reject(error);
    });
});

const app = express();

function XOR_BIT_COUNT(a , b){
    let bitCount = (n)=>{
        let count = BigInt(0);
        while(n){
            count += n & BigInt(1);
            n >>= BigInt(1);
        }
        return count;
    }
    let bigintA = BigInt(a);
    let bigintB = BigInt(b);
    // console.log(bigintA.toString(2).padStart(64,'0'))
    // console.log(bigintB.toString(2).padStart(64,'0'))
    // console.log((bigintA ^ bigintB).toString(2).padStart(64,'0'));
    // console.log(Number(bitCount(bigintA ^ bigintB)));
    // console.log('------------------')
    return Number(bitCount(bigintA ^ bigintB));
}

function IMG_HASH_DISTANCE(a , b){

    const bias = [1 , 1 , 1]


    let distance = 0;
    for(let i = 0 ; i < a.length ; i++){
        distance += XOR_BIT_COUNT(a[i] , b[i]) * bias[i];
    }
    return distance;
}

function cosineSimilarity(vec1, vec2) {
    if (vec1.length !== vec2.length) {
        throw new Error("Vectors must be of the same length");
    }

    const length = vec1.length;
    let dotProduct = 0.0;
    let normVec1 = 0.0;
    let normVec2 = 0.0;

    for (let i = 0; i < length; i++) {
        dotProduct += vec1[i] * vec2[i];
        normVec1 += vec1[i] * vec1[i];
        normVec2 += vec2[i] * vec2[i];
    }

    normVec1 = Math.sqrt(normVec1);
    normVec2 = Math.sqrt(normVec2);

    return normVec1 === 0 || normVec2 === 0 ? 0 : dotProduct / (normVec1 * normVec2);
}

const DB = []

class ImageError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ImageError';
    }

}


const storage = multer.diskStorage({
    destination: function (req, file, cb) {
      cb(null, 'uploads/'); // Make sure this folder exists
    },
    filename: function (req, file, cb) {
        let filename = crypto.randomUUID().replace(/\-/g, '') + path.extname(file.originalname)
      
        cb(null, filename);
        req.filename = 'uploads/' + file.originalname;
    },
    
});
  
const upload = multer({ storage: storage, preservePath: true });

app.post('/uploads', upload.single('image'), async (req, res ,next) => {
    try {


        const result = await imgGenHash(req.file.path);
        const hash = [result.ahash,result.phash,result.dhash];


        // SELECT * FROM TABLE WHERE BIT_COUNT(hash ^ 0x1234567890) * 0.1  > X
        const hashMatches = DB.filter((item) => {
            return IMG_HASH_DISTANCE(hash ,item.hash ) > 0;
        });
        
        
        const featureVector = await imgGenFeatureVector(req.file.path) ;


        const featureVectorMatches = hashMatches.filter((item) => {
            return cosineSimilarity(featureVector ,item.featureVector ) > 1; 
        });

        
        if(featureVectorMatches.length > 0){
            next(new ImageError('Image already exists')) 
            return;
        }

        DB.push({
            hash,
            filename: req.file.filename,
            featureVector
        });
        
      
        res.json({
            hash,
            filename: req.file.filename,
            featureVector,
            link: `http://localhost:3000/uploads/${req.file.filename}`
            
        });
    } catch (error) {
        console.log(error);
        res.sendStatus(500);
    }
});

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.post('/test', async (req, res) => {
    const img1 = req.body.img1;
    const img2 = req.body.img2;

    const [img1_hash, img2_hash] = await  Promise.all([imgGenHash(img1 ),imgGenHash(img2) ] ) ;

    const [img1_vectors, img2_vectors] = await Promise.all( [imgGenFeatureVector(img1) , imgGenFeatureVector(img2)] ) ;

    console.log(img1_hash, img2_hash);
    console.log(img1_vectors, img2_vectors);
    const hash_distance = IMG_HASH_DISTANCE(img1_hash , img2_hash);
    const feature_vector_distance = cosineSimilarity(img1_vectors , img2_vectors);


    console.log('hash_substract : ' , hash_distance);
    console.log('feature_vector_substract : ' , feature_vector_distance);

    res.json({
        hash_distance ,
        feature_vector_distance
    });
});


app.use('/uploads' , express.static('uploads'));



app.use((err, req, res, next) => {
    console.log(err);
    if(req.file){
        fs.unlinkSync(req.file.path);
    }
    if (err instanceof ImageError) {
        res.status(400).json({ error: err.message });
    } else {
        res.sendStatus(500);
    }
})

app.use((req, res, next) => {
    res.sendStatus(404);
});


app.listen(3000, () => {
    console.log('Server is running on port 3000');
});