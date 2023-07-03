const mongoose = require('mongoose');


const fileSchema = new mongoose.Schema({
    path:{}
});

const FileModel = mongoose.model("file",fileSchema);

module.exports = FileModel