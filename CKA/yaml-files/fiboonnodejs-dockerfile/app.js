
const express = require('express');
const ip = require('ip');
const os = require('os');
const app = express();

//使用递归计算菲波那切数列第n项的值
function fibo(n) {
    if (n === 0 || n === 1) return n;
    return fibo(n - 1) + fibo(n - 2);
}

app.get('/', function (req, res) {res.write('I am healthy'); res.end();});
app.get('/fibo/:n', function (req, res){
    var n = parseInt(req.params['n']);
    var f = fibo(n);
    res.write(`Fibo(${n}) = ${f} \n`);
    res.write(`Comupted bu ${os.hostname()} with private IP ${ip.address()}\n`);
    res.end();
});

app.listen(process.env.PORT);