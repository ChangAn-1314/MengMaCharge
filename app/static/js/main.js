const { createApp } = Vue

const app = createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            stations: window.initialData.stations || [],
            loading: false,
            refreshInterval: null,
            lastUpdate: null
        }
    },

    methods: {
        async refreshData() {
            // 不显示加载状态，避免页面闪烁
            try {
                const response = await fetch('/api/stations')
                const data = await response.json()
                if (data.stations) {
                    // 更新每个充电桩的数据
                    data.stations.forEach(newStation => {
                        const index = this.stations.findIndex(s => s.station_id === newStation.station_id)
                        if (index > -1) {
                            // 如果充电桩已存在，只更新其端口数据
                            this.stations[index].ports = newStation.ports
                        } else {
                            // 如果是新的充电桩，添加到列表中
                            this.stations.push(newStation)
                        }
                    })
                    this.lastUpdate = new Date()
                }
            } catch (error) {
                console.error('获取充电桩状态失败:', error)
            }
        },
        formatTime(timestamp) {
            if (!timestamp) return '未知'
            return new Date(timestamp).toLocaleString('zh-CN')
        },
        getLastUpdateTime() {
            return this.lastUpdate ? this.lastUpdate.toLocaleString('zh-CN') : '未知'
        },
        startAutoRefresh() {
            this.refreshInterval = setInterval(() => {
                this.refreshData()
            }, 30000) // 每30秒刷新一次
        },
        stopAutoRefresh() {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval)
            }
        }
    },
    mounted() {
        this.lastUpdate = new Date()
        this.startAutoRefresh()
    },
    beforeUnmount() {
        this.stopAutoRefresh()
    }
}).mount('#app')
