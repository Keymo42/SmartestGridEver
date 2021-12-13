const express = require('express');
const cors = require('cors');
const app = express();
app.use(cors({
    credentials: false
}));
const http = require('http').createServer(app);
const bodyparser = require('body-parser');
// var io = require('socket.io')(http, { 'transports': ['websocket', 'polling'] });


app.use(bodyparser.json());
app.use(bodyparser.urlencoded({ extended: true }));



http.listen(6969, () => {
   console.log('Smartgride Node Server started...');
});

let recent_data = null;

app.get('/', (req, res) => {
    console.log('Test');
    return res.status(200);
});

app.post('/postData', (req, res) => {
    console.log('Test23');
    console.log(recent_data);
    let answer = true;
    if(recent_data === null) recent_data = req.body;
    else answer = false;
    return res.status(200).json(answer);
});

app.get('/getData', (req, res) => {
    const temp = recent_data;
    recent_data = null;
    return res.status(200).json(temp);
});
