document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        alert('请填写所有信息');
        return;
    }
    // 发送请求到后端进行登录验证
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({username: username, password: password})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('登录成功！');
            window.location.href = '/login_success'; // 跳转到登录成功页面
        } else {
            alert('登录失败: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});