const express = require('express');
const bodyParser = require('body-parser');
const sql = require('mssql');

const app = express();
app.use(bodyParser.json());

// 数据库连接配置
const config = {
    user: 'SiiNouBeea',
    password: '114455',
    server: '1210-024',
    database: 'User_All',
    options: {
        encrypt: true,
        trustServerCertificate: false
    }
};

// 连接数据库
sql.connect(config, err => {
    if (err) {
        console.log(err);
    } else {
        console.log('Connected to the database');
    }
});

// 用户注册路由
app.post('/register', async(req, res) => {
    res.sendFile(__dirname + '/网页/register.html');
    const { username, password, nickname, email, phone } = req.body;

    const hashedPassword = await new Promise((resolve, reject) => {
        // 使用bcryptjs加密密码
        const bcrypt = require('bcryptjs');
        bcrypt.hash(password, 10, (err, hash) => {
            if (err) {
                reject(err);
            } else {
                resolve(hash);
            }
        });
    });

    const result = await sql.query `INSERT INTO Users (Username, Password, Nickname, Email, Phone) VALUES (${username}, ${hashedPassword}, ${nickname}, ${email}, ${phone})`;

    res.json({ success: true });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));