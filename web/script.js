document.addEventListener('DOMContentLoaded', () => {
    const categories = ["廢紙", "紙容器", "塑膠", "金屬", "玻璃"];
    // !!! 再次確認：將 YOUR_API_GATEWAY_INVOKE_URL 替換成您正確的 API Gateway 叫用 URL !!!
    const apiUrl = 'https://3vqzh42ba0.execute-api.us-east-1.amazonaws.com/stats'; // 例如：'https://abcdef123.execute-api.us-east-1.amazonaws.com/stats'

    const totalScoreEl = document.getElementById('totalScore');
    const itemsProcessedEl = document.getElementById('itemsProcessed');
    const lastUpdatedEl = document.getElementById('lastUpdated');
    const errorMessageEl = document.getElementById('error-message');
    const refreshButton = document.getElementById('refreshButton');

    async function fetchStats() {
        // 重置為載入中狀態
        totalScoreEl.textContent = '載入中...';
        itemsProcessedEl.textContent = '載入中...';
        errorMessageEl.textContent = ''; // 清除之前的錯誤訊息
        categories.forEach(cat => {
            const el = document.getElementById(`count-${cat}`);
            if (el) el.textContent = '...'; // 讓分類計數也顯示載入中
        });

        try {
            const response = await fetch(apiUrl);
            if (!response.ok) {
                let errorMsg = `HTTP error! status: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.error || errorData.message || errorMsg;
                } catch (e) {
                    // 如果回應不是 JSON，則使用原始狀態碼錯誤
                }
                throw new Error(errorMsg);
            }
            const data = await response.json();

            console.log("Data received from API:", data); // 用於調試

            // 更新各類別數量
            if (data.categories) {
                categories.forEach(cat => {
                    const el = document.getElementById(`count-${cat}`);
                    if (el) {
                        el.textContent = data.categories[cat] !== undefined ? data.categories[cat] : 0;
                    } else {
                        console.warn(`Element with ID count-${cat} not found.`);
                    }
                });
            } else {
                console.warn("API response missing 'categories' field.");
                 categories.forEach(cat => {
                    const el = document.getElementById(`count-${cat}`);
                    if (el) el.textContent = 'N/A';
                });
            }
            
            // 更新總分數
            if (data.totalScore !== undefined) {
                totalScoreEl.textContent = data.totalScore;
            } else {
                console.warn("API response missing 'totalScore' field.");
                totalScoreEl.textContent = 'N/A';
            }

            // 更新已處理回收項目總數 (屬於指定分類的)
            if (data.itemsProcessed !== undefined) {
                itemsProcessedEl.textContent = data.itemsProcessed;
            } else {
                console.warn("API response missing 'itemsProcessed' field.");
                itemsProcessedEl.textContent = 'N/A';
            }
            
            lastUpdatedEl.textContent = `上次更新：${new Date().toLocaleTimeString()}`;

        } catch (error) {
            console.error('Error fetching stats:', error);
            errorMessageEl.textContent = `無法載入數據：${error.message}`;
            // 在錯誤情況下，也設定為錯誤狀態
            totalScoreEl.textContent = '錯誤';
            itemsProcessedEl.textContent = '錯誤';
            categories.forEach(cat => {
                const el = document.getElementById(`count-${cat}`);
                if (el) el.textContent = 'X';
            });
        }
    }

    refreshButton.addEventListener('click', fetchStats);

    // 首次載入時獲取數據
    fetchStats();
});
