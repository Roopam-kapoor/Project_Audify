const express = require ('express');
const bodyParser = require ('body-parser');
const cors = require ('cors');
const path = require ('path');
const multer = require ('multer');
const ffmpeg = require('ffmpeg');
const { spawn } = require('child_process');
const fileUpload = require('express-fileupload');


// constants
const app = express ();
const PORT = process.env.PORT || 5000;

// middleware
app.use (bodyParser.json ());
app.use (bodyParser.urlencoded ({extended: true}));
app.use (cors ());

app.use(
    fileUpload({
        useTempFiles: true,
        tempFileDir:"/public/uploads",
    })
    );

app.post('/convert',(req,res)=>{
    //let to= req.body.to
    let files = req.files.myVideo
    //console.log(to);
    console.log(files);

    files.mv("public/uploads/"+files.name,function(err){
        if(err){
            return res.status(500).send(err);
        }
        console.log("file uploaded");
    });
    try {
        var process = new ffmpeg(`/public/uploads/video.mp4`);
        process.then(function (video) {
            // Callback mode
            video.fnExtractSoundToMP3('/public/result.mp3', function (error, file) {
                if (!error)
                    console.log('Audio file: ' + file);
            });
        }, function (err) {
            console.log('Error: ' + err);
        });
    } catch (e) {
        console.log(e.code);
        console.log(e.msg);
    }
})

// storage engine for multer
const storageEngine = multer.diskStorage ({
  destination: './public/uploads/',
  filename: function (req, file, callback) {
    callback (
      null,
      file.fieldname + '-' + Date.now () + path.extname (file.originalname)
    );
  },
});

  // file filter for multer
 

// initialize multer
const upload = multer ({
  storage: storageEngine,
  
});

// routing
app.post ('/upload', upload.single ('myVideo'), (req, res) => {
  const videoFile = req.file.buffer;
  try{
    
    var process= new ffmpeg('./public/uploads/abc.mp4');
    process.then(function(video){
        video.fnExtractSoundToMP3('/public/result.mp3',function(error,file){
            if(!error){
                console.log('audio file '+ file);
            }
        });
    },function(err){
        console.log('error: '+err);
    });
    process.on("progress", function (progress) {
      console.log("...frames" + progress.frames);})
}
catch(e){
    console.log(e.code);
    console.log(e.msg);
}
    
  

});

  

app.listen (PORT, () => console.log (`Server running on port: ${PORT}`));

