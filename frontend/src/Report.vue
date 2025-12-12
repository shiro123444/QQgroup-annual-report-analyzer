<template>
  <div class="report-page-wrapper">
  <!-- 导出按钮 -->
  <div class="export-btn-wrapper" v-if="report && !exporting">
    <button class="export-btn" @click="exportImage">
      📥 导出图片
    </button>
  </div>
  <div class="export-btn-wrapper" v-if="exporting">
    <div class="export-loading">导出中...</div>
  </div>
  
  <div class="report-container" ref="reportContainer" v-if="report">
    <div class="stripe"></div>
    
    <!-- 头部 -->
    <div class="header">
      <div class="header-badge">Annual Report</div>
      <div class="header-star-group">★ ★ ★</div>
      <h1 :class="getTitleClass(report.chat_name)">{{ report.chat_name }}</h1>
      <div class="subtitle">年度报告</div>
      <div class="header-stats">
        <div class="stat-box">
          <div class="stat-value">{{ formatNumber(report.message_count) }}</div>
          <div class="stat-label">消息总数</div>
        </div>
      </div>
    </div>
    
    <div class="stripe-diagonal"></div>
    
    <!-- 柱状图 -->
    <div class="chart-section">
      <div class="section-header">
        <div class="section-title">热词榜</div>
      </div>
      
      <div class="bar-chart">
        <div v-for="(word, index) in report.selected_words" :key="word.word" class="bar-item">
          <div class="bar-value">{{ word.freq }}</div>
          <div class="bar-wrapper">
            <div class="bar" :style="{ height: word.bar_height + '%' }">
              <div v-for="(seg, segIndex) in word.segments" :key="segIndex"
                   class="bar-segment" 
                   :style="{ height: seg.percent + '%', backgroundColor: seg.color }">
              </div>
            </div>
          </div>
          <div class="bar-label">{{ word.word }}</div>
          <div class="bar-rank">#{{ index + 1 }}</div>
          <div class="bar-contributors">
            <div v-for="(item, itemIndex) in word.legend" :key="itemIndex"
                 :class="['bar-contributor-item', { empty: !item.name }]">
              <div class="bar-contributor-dot" :style="{ background: item.color }"></div>
              <span class="bar-contributor-name">{{ item.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="divider">
      <div class="divider-line"></div>
    </div>
    
    <!-- 热词卡片 -->
    <div class="section">
      <div class="section-header">
        <div class="section-title">热词档案</div>
      </div>
      
      <div class="word-cards">
        <div v-for="(word, index) in report.selected_words" :key="word.word" 
             :class="['word-card', `color-${index + 1}`]">
          <div class="word-card-header">
            <div class="word-card-left">
              <div class="word-card-rank">#{{ index + 1 }}</div>
              <div class="word-card-title">{{ word.word }}</div>
            </div>
            <div class="word-card-freq">{{ word.freq }}次</div>
          </div>
          
          <div v-if="word.ai_comment" class="word-card-comment">{{ word.ai_comment }}</div>
          
          <div class="word-card-contributors">
            {{ word.contributors_text }}
          </div>
          
          <ul class="word-card-samples">
            <li v-for="(sample, sampleIndex) in word.samples.slice(0, 3)" :key="sampleIndex">
              {{ truncateText(sample, 40) }}
            </li>
          </ul>
        </div>
      </div>
    </div>
    
    <div class="stripe"></div>
    
    <!-- 榜单 -->
    <div class="section rankings-section">
      <div class="section-header">
        <div class="section-title">荣誉殿堂</div>
      </div>
      
      <div class="rankings-grid">
        <div v-for="ranking in report.rankings" :key="ranking.title" class="ranking-card">
          <div class="ranking-card-header">
            {{ ranking.icon }} {{ ranking.title }}
          </div>
          
          <div v-if="ranking.first" class="ranking-first">
            <div class="ranking-first-crown">👑</div>
            <img class="ranking-first-avatar" 
                 :src="ranking.first.avatar" 
                 :alt="ranking.first.name"
                 @error="handleImageError">
            <div class="ranking-first-name">{{ ranking.first.name }}</div>
            <div class="ranking-first-value">{{ ranking.first.value }}{{ ranking.unit }}</div>
          </div>
          
          <div v-if="ranking.others" class="ranking-others">
            <div v-for="(item, itemIndex) in ranking.others" :key="itemIndex" class="ranking-item">
              <div class="ranking-item-pos">{{ itemIndex + 2 }}</div>
              <img class="ranking-item-avatar" 
                   :src="item.avatar" 
                   :alt="item.name"
                   @error="handleImageError">
              <div class="ranking-item-name">{{ item.name }}</div>
              <div class="ranking-item-value">{{ item.value }}{{ ranking.unit }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 时段分布 -->
    <div class="section hour-section">
      <div class="section-header">
        <div class="section-title">活跃时段</div>
      </div>
      
      <div class="hour-chart-container">
        <div class="hour-chart">
          <div v-for="(hour, index) in report.statistics?.hourDistribution || {}" :key="index"
               class="hour-bar" :style="{ height: getHourHeight(hour) + '%' }"></div>
        </div>
        <div class="hour-labels">
          <span>0时</span>
          <span>6时</span>
          <span>12时</span>
          <span>18时</span>
          <span>24时</span>
        </div>
        <div class="hour-peak">
          ⭐ 最活跃时段
          <div class="hour-peak-badge">{{ getPeakHour() }}:00 - {{ getPeakHour() + 1 }}:00</div>
        </div>
      </div>
    </div>
    
    <div class="stripe-diagonal"></div>
    
    <!-- 页脚 -->
    <div class="footer">
      <div class="footer-text">
        Github.com/ZiHuixi/QQgroup-annual-report-analyzer
      </div>
    </div>
    
    <div class="stripe-thin"></div>
  </div>
  
  <div v-else-if="loading" class="loading-container">
    <div class="loading">加载中...</div>
  </div>
  
  <div v-else-if="error" class="error-container">
    <div class="error-message">{{ error }}</div>
    <button @click="loadReport">重新加载</button>
  </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import html2canvas from 'html2canvas'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const report = ref(null)
const loading = ref(true)
const error = ref(null)
const exporting = ref(false)
const reportContainer = ref(null)

// 获取路由参数
const getReportId = () => {
  const path = window.location.pathname
  const match = path.match(/\/report\/([^/]+)/)
  return match ? match[1] : null
}

// 加载报告数据
const loadReport = async () => {
  loading.value = true
  error.value = null
  
  try {
    const reportId = getReportId()
    if (!reportId) {
      throw new Error('报告ID不存在')
    }
    
    const { data } = await axios.get(`${API_BASE}/reports/${reportId}`)
    
    if (data.error) {
      throw new Error(data.error)
    }
    
    report.value = data
  } catch (err) {
    error.value = err.message || '加载报告失败'
    console.error('加载报告失败:', err)
  } finally {
    loading.value = false
  }
}

// 格式化数字
const formatNumber = (num) => {
  if (!num) return '0'
  return num.toLocaleString('zh-CN')
}

// 截断文本
const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 获取标题样式类
const getTitleClass = (chatName) => {
  const length = chatName ? chatName.length : 0
  if (length <= 6) return 'short-title'
  if (length <= 15) return 'medium-title'
  if (length <= 24) return 'long-title'
  return 'ultra-long-title'
}

// 处理图片加载错误
const handleImageError = (e) => {
  e.target.style.display = 'none'
}

// 获取时段高度
const getHourHeight = (hour) => {
  if (!hour) return 0
  const maxHour = Math.max(...Object.values(report.value.statistics?.hourDistribution || {}))
  return maxHour > 0 ? (hour / maxHour) * 100 : 0
}

// 获取最活跃时段
const getPeakHour = () => {
  const hourDistribution = report.value.statistics?.hourDistribution || {}
  let maxHour = 0
  let maxValue = 0
  for (const [hour, value] of Object.entries(hourDistribution)) {
    if (value > maxValue) {
      maxValue = value
      maxHour = parseInt(hour)
    }
  }
  return maxHour
}

// 导出为图片
const exportImage = async () => {
  if (!reportContainer.value || exporting.value) return
  
  exporting.value = true
  
  try {
    const canvas = await html2canvas(reportContainer.value, {
      backgroundColor: '#1a1a1a',
      scale: 2,
      useCORS: true,
      allowTaint: true,
      logging: false
    })
    
    // 创建下载链接
    const link = document.createElement('a')
    link.download = `${report.value.chat_name || '群聊'}_年度报告.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  } catch (err) {
    console.error('导出失败:', err)
    alert('导出失败，请重试')
  } finally {
    exporting.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  loadReport()
})
</script>

<style>
/* 导入模板样式 */
@import './report-styles.css';

/* 报告页面包装器 - 居中并设置背景 */
.report-page-wrapper {
  background: #1a1a1a;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 0;
  margin: 0;
  width: 100%;
}

/* 响应式：大屏幕添加内边距 */
@media (min-width: 521px) {
  .report-page-wrapper {
    padding: 20px 0;
  }
}

.loading-container, .error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #1a1a1a;
  color: #F5F5DC;
  width: 100%;
}

.loading {
  font-size: 18px;
  color: #DAA520;
}

.error-message {
  color: #C41E3A;
  margin-bottom: 20px;
}

.error-container button {
  padding: 10px 20px;
  background: #DAA520;
  color: #1a1a1a;
  border: none;
  cursor: pointer;
}

/* 导出按钮 */
.export-btn-wrapper {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.export-btn {
  background: linear-gradient(135deg, #DAA520, #f4c430);
  color: #1a1a1a;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(218, 165, 32, 0.4);
  transition: all 0.3s ease;
}

.export-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(218, 165, 32, 0.5);
}

.export-btn:active {
  transform: translateY(0);
}

.export-loading {
  background: #333;
  color: #DAA520;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
}

/* 移动端导出按钮位置调整 */
@media (max-width: 520px) {
  .export-btn-wrapper {
    top: 10px;
    right: 10px;
  }
  
  .export-btn, .export-loading {
    padding: 10px 16px;
    font-size: 13px;
  }
}
</style>
