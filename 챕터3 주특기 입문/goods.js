// schemas
const mongoose = require("mongoose");

const goodsSchema = mongoose.Schema({
    goodsId: {
        type:Number,
        required: true,
        unique: true,
    },
    name : {
        type: String,
        required: true,
        unique: true,
    },
    thumbnailUrl:{
        type: String,
    },
    category : { // 여기 category가 있기 때문에 routes/goods.js에서 찾을 수 있는거임
        type: String,
    },
    Price: {
        type:Number,
    },
});

module.exports = mongoose.model("Goods", goodsSchema);
