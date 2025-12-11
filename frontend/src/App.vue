<template>
  <div class="container">
    <div class="card">
      <h2>QQ群年度报告分析器（Web）</h2>
      <p>上传 qq-chat-exporter 导出的 JSON，选择参数，点击分析。</p>
      <div class="flex" style="margin-top: 12px;">
        <input type="file" accept=".json" @change="onFileChange" />
        <button :disabled="loading || !file" @click="startAnalyze">开始分析</button>
        <span v-if="loading">⏳ 正在分析...</span>
      </div>
    </div>

    <div class="card">
      <h3>可调参数</h3>
      <div class="grid">
        <div>
          <label>TOP_N 热词</label><br />
          <input type="number" v-model.number="options.TOP_N" min="10" />
        </div>
        <div>
          <label>新词最小频次</label><br />
          <input type="number" v-model.number="options.NEW_WORD_MIN_FREQ" min="1" />
        </div>
        <div>
          <label>PMI 阈值</label><br />
          <input type="number" step="0.1" v-model.number="options.PMI_THRESHOLD" />
        </div>
        <div>
          <label>熵阈值</label><br />
          <input type="number" step="0.1" v-model.number="options.ENTROPY_THRESHOLD" />
        </div>
        <div>
          <label>合并最小频次</label><br />
          <input type="number" v-model.number="options.MERGE_MIN_FREQ" min="1" />
        </div>
        <div>
          <label>合并条件概率</label><br />
          <input type="number" step="0.05" v-model.number="options.MERGE_MIN_PROB" />
        </div>
        <div>
          <label>导出图片</label><br />
          <input type="checkbox" v-model="options.ENABLE_IMAGE_EXPORT" />
          <span class="tag">需服务器有 chromium</span>
        </div>
        <div>
          <label>生成 PNG</label><br />
          <input type="checkbox" v-model="options.GENERATE_PNG" :disabled="!options.ENABLE_IMAGE_EXPORT" />
        </div>
      </div>
    </div>

    <div v-if="result" class="card">
      <h3>分析结果</h3>
      <div class="flex">
        <div class="badge">群聊：{{ result.chatName }}</div>
        <div class="badge">消息数：{{ result.messageCount }}</div>
      </div>

      <h4 style="margin-top: 12px;">热词 Top 10</h4>
      <ol>
        <li v-for="item in result.topWords.slice(0, 10)" :key="item.word">
          {{ item.word }} - {{ item.freq }} 次
        </li>
      </ol>

      <h4>榜单概览</h4>
      <div class="grid">
        <div v-for="(items, title) in result.rankings" :key="title" class="card" style="padding: 12px;">
          <strong>{{ title }}</strong>
          <div v-if="items && items.length">
            <div>{{ items[0].name }} ({{ items[0].value || items[0][1] }})</div>
          </div>
          <div v-else>无数据</div>
        </div>
      </div>

      <div class="flex" style="margin-top: 12px;" v-if="downloadsAvailable">
        <a v-if="downloadLinks.txt" :href="downloadLinks.txt" download>下载文本报告</a>
        <a v-if="downloadLinks.html" :href="downloadLinks.html" download>下载HTML</a>
        <a v-if="downloadLinks.png" :href="downloadLinks.png" download>下载图片</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { reactive, ref, computed } from 'vue'

const file = ref(null)
const loading = ref(false)
const result = ref(null)
const serverPaths = ref({ txt: null, html: null, png: null })

const options = reactive({
  TOP_N: 200,
  NEW_WORD_MIN_FREQ: 20,
  PMI_THRESHOLD: 2.0,
  ENTROPY_THRESHOLD: 0.5,
  MERGE_MIN_FREQ: 30,
  MERGE_MIN_PROB: 0.3,
  ENABLE_IMAGE_EXPORT: false,
  GENERATE_PNG: true
})

const downloadsAvailable = computed(() => serverPaths.value.txt || serverPaths.value.html || serverPaths.value.png)
const downloadLinks = computed(() => ({
  txt: serverPaths.value.txt ? `/api/download?path=${encodeURIComponent(serverPaths.value.txt)}` : null,
  html: serverPaths.value.html ? `/api/download?path=${encodeURIComponent(serverPaths.value.html)}` : null,
  png: serverPaths.value.png ? `/api/download?path=${encodeURIComponent(serverPaths.value.png)}` : null
}))

const onFileChange = (e) => {
  const [f] = e.target.files || []
  file.value = f || null
}

const startAnalyze = async () => {
  if (!file.value) return
  loading.value = true
  result.value = null
  serverPaths.value = { txt: null, html: null, png: null }
  try {
    const form = new FormData()
    form.append('file', file.value)
    form.append('options', JSON.stringify(options))
    const { data } = await axios.post('/api/analyze', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000
    })
    if (data.error) throw new Error(data.error)
    result.value = data.result
    serverPaths.value = {
      txt: data.txt_report || null,
      html: data.html_report || null,
      png: data.png_report || null
    }
  } catch (err) {
    const respErr = err?.response?.data?.error
    const msg = respErr ? `分析失败: ${respErr}` : `分析失败: ${err.message || '未知错误'}`
    alert(msg)
  } finally {
    loading.value = false
  }
}
</script>

