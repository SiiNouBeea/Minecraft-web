document.getElementById('registerForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const nickname = document.getElementById('nickname').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;

    // 检查所有字段是否填写
    if (!username || !password || !nickname || !email || !phone) {
        alert('请填写所有信息');
        return;
    }

    // 发送请求到后端进行登录验证
    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({username: username, email: email, phone: phone})
    })
    .then(data => {
        if (!data.success) {
            if (data.error) {
                document.getElementById('username-error').style.display = 'inline';
                document.getElementById('username-error').textContent = data.error;
            } else if (data.error.includes('账户已存在')) {
                document.getElementById('username-error').style.display = 'inline';
                document.getElementById('username-error').textContent = data.error;
            } else if (data.error.includes('邮箱已注册')) {
                document.getElementById('email-error').style.display = 'inline';
                document.getElementById('email-error').textContent = data.error;
            } else if (data.error.includes('手机号已注册')) {
                document.getElementById('phone-error').style.display = 'inline';
                document.getElementById('phone-error').textContent = data.error;
            }
        })
    .catch(error => {
        console.error('Error:', error);
    });
});