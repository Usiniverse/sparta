const express = require("express")
const connect = require("./schemas")
const app = express();
const port = 3000;

connect();

const goodsRouter = require("./routes/goods");

const requestMiddleware = (req, res, next) => {
    console.log("Request URL", req.originalURl, " - ", new Date());
    next();
}

app.use(express.json());
app.use(requestMiddleware);

app.use("/api", [goodsRouter]);

app.get("/",(req, res) => {
    res.send("Hello World");
});

app.listen(port, () => {
    console.log(port, "포트로 서버가 켜졌어요!");
});
