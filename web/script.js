document.addEventListener('DOMContentLoaded', () => {
    const categories = ["廢紙", "紙容器", "塑膠", "金屬", "玻璃"];
    // !!! 再次確認：將 YOUR_API_GATEWAY_INVOKE_URL 替換成您正確的 API Gateway 叫用 URL !!!
    const apiUrl = 'https://3vqzh42ba0.execute-api.us-east-1.amazonaws.com/stats'; // 例如：'https://abcdef123.execute-api.us-east-1.amazonaws.com/stats'
    const statusUrl = 'https://3vqzh42ba0.execute-api.us-east-1.amazonaws.com/status'; // 例如：'https://abcdef123.execute-api.us-east-1.amazonaws.com/stats'
    const totalScoreEl = document.getElementById('totalScore');
    const itemsProcessedEl = document.getElementById('itemsProcessed');
    const lastUpdatedEl = document.getElementById('lastUpdated');
    const errorMessageEl = document.getElementById('error-message');
    const refreshButton = document.getElementById('refreshButton');

    // 統計資料
    async function fetchStats() {
        totalScoreEl.textContent = '載入中...';
        itemsProcessedEl.textContent = '載入中...';
        errorMessageEl.textContent = '';
        categories.forEach(cat => {
            const el = document.getElementById(`count-${cat}`);
            if (el) el.textContent = '...';
        });
        try {
            const response = await fetch(apiUrl);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            // 更新各類別數量
            if (data.categories) {
                categories.forEach(cat => {
                    const el = document.getElementById(`count-${cat}`);
                    if (el) el.textContent = data.categories[cat] !== undefined ? data.categories[cat] : 0;
                });
            }
            // 更新總分數
            totalScoreEl.textContent = data.totalScore !== undefined ? data.totalScore : 'N/A';
            // 同步更新點數兌換頁面分數
            const currentScoreEl = document.getElementById('currentScore');
            if (currentScoreEl) currentScoreEl.textContent = data.totalScore !== undefined ? data.totalScore : 'N/A';
            // 更新已處理回收項目總數
            itemsProcessedEl.textContent = data.itemsProcessed !== undefined ? data.itemsProcessed : 'N/A';
            lastUpdatedEl.textContent = `上次更新：${new Date().toLocaleTimeString()}`;
        } catch (error) {
            errorMessageEl.textContent = `無法載入數據：${error.message}`;
            totalScoreEl.textContent = '錯誤';
            itemsProcessedEl.textContent = '錯誤';
            categories.forEach(cat => {
                const el = document.getElementById(`count-${cat}`);
                if (el) el.textContent = 'X';
            });
        }
    }

    // 設備狀態
    async function fetchDeviceStatus() {
        try {
            const response = await fetch(statusUrl);
            const data = await response.json();
            // 判斷在線/離線
            const now = Math.floor(Date.now() / 1000);
            const isOnline = (now - data.timestamp) < 300;
            document.getElementById('deviceStatus').textContent = isOnline ? '在線' : '離線';
            document.getElementById('lastConnection').textContent = `最後連線時間：${new Date(data.timestamp * 1000).toLocaleString()}`;
            document.getElementById('statusDot').classList.toggle('online', isOnline);
            const deviceStateElement = document.getElementById('deviceState');
            deviceStateElement.textContent = `狀態：${data.status}`;
            deviceStateElement.style.color = {
                'idle': '#50d06c',
                'capturing': '#007bff',
                'uploading': '#ff9800',
                'error': '#e53935'
            }[data.status] || '#333';
        } catch (e) {
            document.getElementById('deviceStatus').textContent = '未知';
            document.getElementById('lastConnection').textContent = '';
            document.getElementById('statusDot').classList.remove('online');
            document.getElementById('deviceState').textContent = '';
        }
    }

    // 綁定刷新按鈕
    refreshButton.addEventListener('click', () => {
        fetchStats();
        fetchDeviceStatus();
    });

    // 頁面載入時自動刷新
    fetchStats();
    fetchDeviceStatus();

    // 模擬用戶數據
    const mockUsers = {
        'admin': 'password123',
        'vaclis':'vaclis'
    };

    // 模擬設備狀態
    let deviceStatus = {
        online: false,
        lastConnection: null
    };

    // DOM 元素
    const loginForm = document.getElementById('loginForm');
    const mainContent = document.getElementById('mainContent');
    const login = document.getElementById('login');
    const logoutBtn = document.getElementById('logoutBtn');
    const navBtns = document.querySelectorAll('.nav-btn');
    const pages = document.querySelectorAll('.page');
    const deviceStatusElement = document.getElementById('deviceStatus');
    const lastConnectionElement = document.getElementById('lastConnection');
    const statusDot = document.querySelector('.status-dot');

    // 登入處理
    login.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (mockUsers[username] === password) {
            loginForm.style.display = 'none';
            mainContent.style.display = 'block';
            localStorage.setItem('isLoggedIn', 'true');
            fetchDeviceStatus();
        } else {
            alert('使用者名稱或密碼錯誤');
        }
    });

    // 登出處理
    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('isLoggedIn');
        loginForm.style.display = 'block';
        mainContent.style.display = 'none';
        document.getElementById('username').value = '';
        document.getElementById('password').value = '';
    });

    // 頁面切換
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetPage = btn.dataset.page;
            
            // 更新按鈕狀態
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // 更新頁面顯示
            pages.forEach(page => {
                page.classList.remove('active');
                if (page.id === targetPage) {
                    page.classList.add('active');
                }
            });
        });
    });

    // 點數兌換處理
    document.querySelectorAll('.redeem-btn').forEach((btn, index) => {
        btn.addEventListener('click', () => {
            const reward = rewards[index];
            const totalScore = parseInt(document.getElementById('totalScore').textContent);
            
            if (totalScore >= reward.points) {
                if (confirm(`確定要兌換 ${reward.name} 嗎？將扣除 ${reward.points} 點`)) {
                    alert('兌換成功！');
                    // 這裡可以添加實際的兌換邏輯
                }
            } else {
                alert('點數不足！');
            }
        });
    });

    // 檢查登入狀態
    function checkLoginStatus() {
        if (localStorage.getItem('isLoggedIn') === 'true') {
            loginForm.style.display = 'none';
            mainContent.style.display = 'block';
            fetchDeviceStatus();
        }
    }

    // 初始化
    checkLoginStatus();
});
