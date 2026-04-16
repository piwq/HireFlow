<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import html2pdf from 'html2pdf.js'
import { Wand2, Download, ChevronRight, ChevronLeft, Loader2, FileText, Sparkles, PenTool, LayoutTemplate, Save, Check, RefreshCw, Eye, ArrowLeft } from 'lucide-vue-next'

const loading = ref(false)
const error = ref('')
const isStreamingDone = ref(false)
const savingStatus = ref('') // '', 'saving', 'saved'
const windowWidth = ref(window.innerWidth)

const questions = [
  "Какая у вас желаемая должность?",
  "Опишите ваш последний опыт работы. Чем вы там занимались?",
  "Какими ключевыми навыками и технологиями вы владеете?",
  "Вставьте описание целевой вакансии для ATS-оптимизации (Необязательно)"
]
const currentStep = ref(0)
const answers = ref(['', '', '', ''])

const streamedMarkdown = ref('')
const streamedHtml = ref('')
const resumeContentRef = ref(null)
const questionInputRef = ref(null)

// Editor state
const editorMode = ref('ai') // 'ai' or 'manual'
const aiPrompt = ref('')
const currentTheme = ref('classic') // 'classic' or 'tech'
const showMobilePreview = ref(false)
const showResetConfirmation = ref(false)

const canProceed = computed(() => {
  if (currentStep.value === 3) return true
  return answers.value[currentStep.value].trim().length > 0
})

const canEnhance = computed(() => {
  return aiPrompt.value.trim().length > 0
})

let saveTimeout = null
watch(streamedMarkdown, (newVal) => {
  if (isStreamingDone.value && !loading.value) {
    streamedHtml.value = DOMPurify.sanitize(marked.parse(newVal))
    
    savingStatus.value = 'saving'
    clearTimeout(saveTimeout)
    saveTimeout = setTimeout(async () => {
        if (newVal.trim().length > 0) {
            try {
                const token = localStorage.getItem('token')
                await fetch('/api/candidates/ai/save-draft', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                    },
                    body: JSON.stringify({ content: newVal })
                })
                savingStatus.value = 'saved'
                setTimeout(() => { savingStatus.value = '' }, 2000)
            } catch(e) {
                console.error("Draft save failed")
            }
        }
    }, 1500)
  }
})

async function forceSaveDraft() {
   if (!streamedMarkdown.value) return;
   const token = localStorage.getItem('token')
   await fetch('/api/candidates/ai/save-draft', {
      method: 'POST',
      headers: {
         'Content-Type': 'application/json',
         ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify({ content: streamedMarkdown.value })
   })
}

async function loadDraft() {
    const token = localStorage.getItem('token')
    if (!token) return

    try {
        const res = await fetch('/api/candidates/ai/draft', {
            headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
            const data = await res.json()
            if (data.content && data.content.trim().length > 0) {
                streamedMarkdown.value = data.content
                streamedHtml.value = DOMPurify.sanitize(marked.parse(data.content))
                isStreamingDone.value = true
            }
        }
    } catch(e) {
        console.error("Failed to load draft")
    }
}

async function startStream() {
  loading.value = true
  isStreamingDone.value = false
  streamedMarkdown.value = ''
  streamedHtml.value = ''
  error.value = ''
  
  try {
    const token = localStorage.getItem('token')
    streamedHtml.value = '<div class="absolute inset-0 flex flex-col items-center justify-center text-indigo-500/50"><span class="animate-pulse flex items-center gap-2 font-medium">Адаптируем под ATS системы...</span></div>'
    
    const response = await fetch('/api/candidates/ai/generate-stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ answers: answers.value })
    })

    if (!response.ok) throw new Error('Network error')
    streamedHtml.value = ''
    const reader = response.body.getReader()
    const decoder = new TextDecoder("utf-8")

    while (true) {
        const { value, done } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        streamedMarkdown.value += chunk
        streamedHtml.value = marked.parse(streamedMarkdown.value)
    }

    isStreamingDone.value = true
    await forceSaveDraft()
  } catch (err) {
    error.value = 'Ошибка генерации резюме.'
    streamedHtml.value = ''
  } finally {
    loading.value = false
  }
}

async function focusTextarea() {
  await nextTick()
  // Add a tiny delay to ensure transition doesn't interfere with focus
  setTimeout(() => {
    if (questionInputRef.value) {
      questionInputRef.value.focus()
    }
  }, 50)
}

async function enhanceStream() {
  if (!canEnhance.value || loading.value) return
  loading.value = true
  error.value = ''
  const previousMarkdown = streamedMarkdown.value
  streamedMarkdown.value = ''
  
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('/api/candidates/ai/enhance-stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ current_content: previousMarkdown, prompt: aiPrompt.value })
    })

    if (!response.ok) throw new Error('Network error')
    aiPrompt.value = '' 
    const reader = response.body.getReader()
    const decoder = new TextDecoder("utf-8")

    while (true) {
        const { value, done } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        streamedMarkdown.value += chunk
        streamedHtml.value = marked.parse(streamedMarkdown.value)
    }
    await forceSaveDraft()
  } catch (err) {
    error.value = 'Ошибка обновления резюме.'
    streamedMarkdown.value = previousMarkdown
    streamedHtml.value = marked.parse(previousMarkdown)
  } finally {
    loading.value = false
  }
}

function nextStep() {
  if (!canProceed.value || loading.value) return
  if (currentStep.value < questions.length - 1) {
    currentStep.value++
    focusTextarea()
  } else {
    startStream()
  }
}

function prevStep() {
  if (currentStep.value > 0 && !loading.value) {
    currentStep.value--
    focusTextarea()
  }
}

async function exportPdf() {
  if (!resumeContentRef.value) return
  error.value = ''
  
  // Clone the entire A4 container to keep theme classes
  const element = resumeContentRef.value
  const clone = element.cloneNode(true)
  
  // CRITICAL: Reset transform/scale for PDF generation
  clone.style.transform = 'none'
  clone.style.width = '210mm'
  clone.style.minHeight = '297mm'
  clone.style.margin = '0'
  clone.style.position = 'relative'
  clone.style.left = '0'
  clone.style.top = '0'
  
  const pulseEls = clone.querySelectorAll('.animate-pulse')
  pulseEls.forEach(el => el.remove())

  // Hide the "empty resume" placeholder in PDF just in case
  const emptyPlaceholder = clone.querySelector('.absolute.inset-0.flex.flex-col')
  if (emptyPlaceholder) emptyPlaceholder.remove()

  const opt = {
      margin: 10,  // Add some margin for safety
      filename: `resume_${currentTheme.value}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { 
        scale: 2, 
        useCORS: true,
        letterRendering: true,
        logging: false
      },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
      pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
  }
  
  try {
    await html2pdf().from(clone).set(opt).save()
  } catch(err) {
    console.error('PDF error:', err)
    error.value = 'Не удалось собрать PDF'
  }
}

async function resetResume() {
  showResetConfirmation.value = false
  
  answers.value = ['', '', '', '']
  currentStep.value = 0
  streamedMarkdown.value = ''
  streamedHtml.value = ''
  isStreamingDone.value = false
  error.value = ''
  focusTextarea()
  const token = localStorage.getItem('token')
  if (token) {
    await fetch('/api/candidates/ai/save-draft', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ content: '' })
    }).catch(() => {})
  }
}

const handleResize = () => { windowWidth.value = window.innerWidth }

onMounted(() => {
  marked.setOptions({ breaks: true })
  window.addEventListener('resize', handleResize)
  loadDraft()
  if (!isStreamingDone.value) {
    focusTextarea()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="h-full flex flex-col bg-brand-light-base dark:bg-brand-dark-base antialiased">
      
      <!-- Top Header -->
      <div class="p-4 md:px-8 md:py-6 shrink-0 flex items-center justify-between border-b border-brand-light-border dark:border-brand-dark-border bg-brand-light-surface dark:bg-brand-dark-surface z-10 w-full relative drop-shadow-sm">
        <div class="flex items-center gap-4">
          <RouterLink to="/candidate" class="p-2.5 rounded-xl hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated text-brand-light-muted dark:text-brand-dark-muted transition-colors mr-2">
            <ArrowLeft class="w-6 h-6" />
          </RouterLink>
          <div class="w-10 h-10 md:w-12 md:h-12 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center border border-indigo-500/10 shadow-inner">
            <Wand2 class="w-5 h-5 md:w-6 md:h-6 text-indigo-500 dark:text-indigo-400" />
          </div>
          <div>
            <h1 class="text-xl md:text-display text-brand-light-primary dark:text-brand-dark-primary font-bold tracking-tight">ИИ-Конструктор</h1>
            <p class="hidden md:block text-sm text-brand-light-secondary dark:text-brand-dark-secondary mt-0.5 font-medium">
              {{ isStreamingDone ? 'Настройте и улучшите сгенерированное резюме.' : 'Ответьте на вопросы, и ИИ создаст идеальное резюме.' }}
            </p>
          </div>
        </div>

        <div class="flex items-center gap-3">
           <div v-if="savingStatus === 'saving'" class="hidden md:flex text-gray-400 text-xs items-center gap-2">
             <Loader2 class="w-3 h-3 animate-spin" /> Сохранение
           </div>
           
           <button 
             v-if="isStreamingDone"
             @click="showMobilePreview = !showMobilePreview"
             class="lg:hidden p-3 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-xl text-brand-light-primary dark:text-brand-dark-primary shadow-sm"
           >
             <Eye v-if="!showMobilePreview" class="w-5 h-5" />
             <PenTool v-else class="w-5 h-5" />
           </button>

           <button 
             v-if="isStreamingDone"
             @click="exportPdf"
             class="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl px-4 py-2.5 md:px-6 md:py-3 font-bold text-xs md:text-sm transition-all shadow-lg flex items-center gap-2"
           >
             <Download class="w-4 h-4 md:w-5 md:h-5" /> <span class="hidden sm:inline">PDF</span>
           </button>
        </div>
      </div>

      <!-- Split Layout -->
      <div class="flex-1 flex overflow-hidden w-full relative">
        
        <!-- Left Panel: Q&A Wizard OR Editor -->
        <div 
          v-show="!showMobilePreview || !isStreamingDone"
          class="w-full lg:w-1/2 p-6 md:p-12 overflow-y-auto bg-brand-light-surface dark:bg-[#121212] border-r border-brand-light-border dark:border-brand-dark-border flex flex-col relative drop-shadow-sm z-10"
        >
          
          <!-- STATE 1: GENERATION WIZARD -->
          <div v-if="!isStreamingDone" class="max-w-xl mx-auto w-full pt-4">
            <div class="flex items-center gap-3 mb-10">
              <div v-for="(q, idx) in questions" :key="idx" class="h-2.5 flex-1 rounded-full transition-all duration-700 bg-gray-200 dark:bg-gray-800 relative overflow-hidden">
                <div 
                   class="absolute top-0 left-0 h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-700"
                   :style="{ width: idx < currentStep ? '100%' : '0%' }"
                ></div>
              </div>
            </div>

            <transition name="slide-up" mode="out-in" @after-enter="focusTextarea">
              <div :key="currentStep" class="mb-10 min-h-[260px]">
                <h4 class="text-2xl md:text-3xl font-bold text-brand-light-primary dark:text-brand-dark-primary leading-tight mb-8">
                  <span class="text-indigo-500 mr-2 text-xs uppercase tracking-widest font-black block mb-4 border-b border-indigo-500/20 pb-2 w-max">ШАГ {{ currentStep + 1 }} ИЗ {{ questions.length }}</span>
                  {{ questions[currentStep] }}
                </h4>
                
                <textarea
                  ref="questionInputRef"
                  v-model="answers[currentStep]"
                  rows="7"
                  :placeholder="currentStep === 3 ? 'Вставьте текст вакансии сюда...' : 'Расскажите подробнее...'"
                  class="w-full bg-white dark:bg-[#1a1a1a] border border-gray-200 dark:border-gray-800 rounded-3xl px-6 py-5 text-body text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-medium resize-none shadow-sm text-lg leading-relaxed"
                  @keydown.ctrl.enter="nextStep"
                />
              </div>
            </transition>

            <div v-if="error" class="mb-8 p-5 bg-red-500/10 text-red-600 rounded-xl border border-red-500/20 text-sm font-medium flex items-center gap-3">
              <div class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
              {{ error }}
            </div>

            <div class="flex items-center justify-between pt-6 border-t border-gray-100 dark:border-gray-800/60 mt-auto">
              <button 
                @click="prevStep"
                :class="currentStep === 0 ? 'opacity-0 pointer-events-none' : 'opacity-100'"
                class="flex items-center gap-2 px-5 py-3.5 text-gray-500 hover:text-gray-900 transition-all font-bold rounded-2xl hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                <ChevronLeft class="w-5 h-5" /> Назад
              </button>

              <button 
                @click="nextStep"
                :disabled="!canProceed || loading"
                class="bg-brand-light-primary dark:bg-white hover:bg-black text-white dark:text-black rounded-2xl px-8 py-4 text-body font-bold transition-all shadow-lg flex items-center gap-2 disabled:opacity-40"
              >
                <template v-if="loading && currentStep === questions.length - 1">
                  <Loader2 class="w-5 h-5 animate-spin" /> Анализ...
                </template>
                <template v-else>
                  {{ currentStep === questions.length - 1 ? (answers[3] ? 'Оптимизировать ATS' : 'Сгенерировать резюме') : 'Следующий шаг' }}
                  <ChevronRight class="w-5 h-5" />
                </template>
              </button>
            </div>
          </div>

          <!-- STATE 2: INTERACTIVE EDITOR -->
          <div v-else class="max-w-2xl mx-auto w-full flex flex-col h-full animate-[fadeIn_0.5s_ease-out]">
            <div class="flex items-center justify-between mb-8">
               <div class="flex items-center gap-4">
                 <h3 class="text-2xl font-black text-brand-light-primary dark:text-brand-dark-primary">Редактор</h3>
                 <button @click="showResetConfirmation = true" class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-500/10 text-red-500 text-xs font-bold hover:bg-red-500/20 transition-all uppercase tracking-widest">
                   <RefreshCw class="w-3.5 h-3.5" /> Сбросить
                 </button>
               </div>
               <div class="flex items-center gap-2 bg-gray-100 dark:bg-gray-800/80 p-1 rounded-xl border border-gray-200 dark:border-gray-700">
                  <button @click="currentTheme = 'classic'" class="px-3 py-1 rounded-lg text-xs font-bold transition-all" :class="currentTheme === 'classic' ? 'bg-white dark:bg-neutral-900 text-indigo-600 shadow-sm' : 'text-gray-500 hover:text-gray-800'">Классика</button>
                  <button @click="currentTheme = 'tech'" class="px-3 py-1 rounded-lg text-xs font-bold transition-all" :class="currentTheme === 'tech' ? 'bg-white dark:bg-neutral-900 text-emerald-600 shadow-sm' : 'text-gray-500 hover:text-gray-800'">Tech IT</button>
               </div>
            </div>

            <div class="flex bg-gray-100 dark:bg-gray-800/80 p-1.5 rounded-2xl mb-6 shrink-0 relative z-10 w-max shadow-inner">
               <button @click="editorMode = 'ai'" class="flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-sm transition-all" :class="editorMode === 'ai' ? 'bg-white dark:bg-neutral-900 text-indigo-600 shadow-sm' : 'text-gray-500 hover:text-gray-800'"><Sparkles class="w-4 h-4" /> ИИ-Промпт</button>
               <button @click="editorMode = 'manual'" class="flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-sm transition-all" :class="editorMode === 'manual' ? 'bg-white dark:bg-neutral-900 text-indigo-600 shadow-sm' : 'text-gray-500 hover:text-gray-800'"><PenTool class="w-4 h-4" /> Ручной режим</button>
            </div>

            <div v-if="editorMode === 'manual'" class="flex-1 flex flex-col min-h-0 relative">
               <textarea v-model="streamedMarkdown" class="flex-1 w-full bg-white dark:bg-[#1a1a1a] border border-gray-200 dark:border-gray-800 rounded-3xl p-6 text-sm font-mono text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 resize-none leading-relaxed shadow-sm" placeholder="Markdown текст..."></textarea>
               <p class="text-xs text-gray-400 mt-4 text-center">Прямое редактирование Markdown. Идет постоянное автосохранение.</p>
            </div>

            <div v-if="editorMode === 'ai'" class="flex flex-col flex-1">
               <div class="bg-indigo-50 dark:bg-indigo-900/10 border border-indigo-100 dark:border-indigo-500/20 rounded-3xl p-6 mb-8 text-indigo-900 dark:text-indigo-200 text-sm leading-relaxed shadow-inner font-medium">
                  <strong>Как работает ИИ-помощник?</strong> <br><br> Напиши, что именно ты хочешь переделать в текущем резюме. Например:<br>
                  <em class="opacity-80 block mt-2 ml-4">«Сделай текст более агрессивно продающим»</em>
                  <em class="opacity-80 block mt-1 ml-4">«Добавь в навыки Docker и Kubernetes»</em>
               </div>
               <textarea v-model="aiPrompt" rows="6" placeholder="Что нужно улучшить или изменить?" class="w-full bg-white dark:bg-[#1a1a1a] border border-gray-200 dark:border-gray-800 rounded-3xl px-6 py-5 text-body text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-medium resize-none shadow-sm text-lg leading-relaxed" @keydown.ctrl.enter="enhanceStream" />
               <div class="flex items-center justify-end mt-4">
                 <button @click="enhanceStream" :disabled="!canEnhance || loading" class="bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl px-8 py-3.5 text-body font-bold transition-all shadow-lg flex items-center gap-2 disabled:opacity-40">
                    <template v-if="loading"><Loader2 class="w-5 h-5 animate-spin" /> Обновляем...</template>
                    <template v-else><Sparkles class="w-4 h-4" /> Выполнить</template>
                 </button>
               </div>
            </div>
          </div>
        </div>

        <!-- Right Panel: Live A4 Preview -->
        <div :class="['w-full lg:w-1/2 bg-[#e2e8f0] dark:bg-[#0a0a0a] overflow-y-auto p-4 md:p-10 flex flex-col items-center relative shadow-[inset_10px_0_20px_rgba(0,0,0,0.03)] z-0 transition-all duration-300', showMobilePreview ? 'flex fixed inset-0 z-50 lg:static' : 'hidden lg:flex']">
           <div v-if="loading" class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-white/30 dark:bg-black/30 backdrop-blur-sm transition-all duration-500">
             <div class="bg-white/95 dark:bg-neutral-900/95 backdrop-blur-xl px-8 py-5 rounded-3xl shadow-2xl flex items-center gap-4 border border-indigo-500/20 ring-1 ring-black/5">
                <Loader2 class="w-6 h-6 text-indigo-500 animate-spin" />
                <span class="font-bold text-lg text-indigo-900 dark:text-indigo-100">Нейросеть печатает...</span>
             </div>
           </div>

           <!-- A4 Page Container -->
           <div ref="resumeContentRef" class="bg-white text-black shrink-0 shadow-2xl relative overflow-hidden transition-all duration-500 ring-1 ring-gray-900/5 my-auto print-container origin-top lg:scale-100" :class="`theme-${currentTheme}`" :style="{ width: '210mm', minHeight: '297mm', padding: '20mm 30mm', transform: 'scale(' + (windowWidth < 1024 ? (windowWidth / 900) : 1) + ')' }">
              <div class="w-full h-full relative z-0">
                 <div v-if="!streamedHtml && !loading" class="absolute inset-0 flex flex-col items-center justify-center text-gray-300 transition-opacity duration-500">
                    <div class="w-32 h-32 rounded-[2rem] border-2 border-dashed border-gray-200 dark:border-gray-800 flex items-center justify-center mb-6 bg-gray-50/50 shadow-inner"><FileText class="w-16 h-16 text-gray-300" /></div>
                    <p class="text-2xl font-bold text-gray-400">Резюме пусто</p>
                    <p class="text-sm text-gray-400 mt-2 font-medium text-center">Заполните анкету слева, чтобы ИИ сотворил магию</p>
                 </div>
                <div v-html="streamedHtml" class="rendered-markdown break-words"></div>
                <span v-if="loading && streamedHtml" class="inline-block w-2.5 h-6 bg-indigo-500 animate-pulse mt-0.5 ml-1 align-bottom shadow-[0_0_8px_rgba(99,102,241,0.6)]"></span>
              </div>
           </div>
        </div>
      </div>

      <!-- Custom Reset Modal -->
      <transition name="fade">
        <div v-if="showResetConfirmation" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showResetConfirmation = false"></div>
          <div class="relative bg-white dark:bg-brand-dark-surface p-8 rounded-[2.5rem] shadow-2xl max-w-md w-full border border-brand-light-border dark:border-brand-dark-border animate-[slideUp_0.3s_ease-out]">
            <div class="w-20 h-20 bg-red-100 dark:bg-red-500/10 rounded-3xl flex items-center justify-center mb-6 mx-auto">
              <RefreshCw class="w-10 h-10 text-red-500 animate-[spin_3s_linear_infinite]" />
            </div>
            <h3 class="text-2xl font-black text-brand-light-primary dark:text-brand-dark-primary text-center mb-3">Сбросить резюме?</h3>
            <p class="text-brand-light-secondary dark:text-brand-dark-secondary text-center mb-8 font-medium">
              Все ваши ответы и сгенерированный текст будут безвозвратно удалены. Вы уверены?
            </p>
            <div class="flex flex-col gap-3">
              <button 
                @click="resetResume"
                class="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-4 rounded-2xl shadow-lg shadow-red-500/20 transition-all active:scale-95"
              >
                Да, сбросить всё
              </button>
              <button 
                @click="showResetConfirmation = false"
                class="w-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-brand-light-primary dark:text-brand-dark-primary font-bold py-4 rounded-2xl transition-all active:scale-95"
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      </transition>
  </div>
</template>

<style scoped>
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.98);
}
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.98);
}

/* =========================================
   THEME: CLASSIC (Default Corporate)
   ========================================= */
.theme-classic {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

.theme-classic :deep(.rendered-markdown) {
  color: #111827 !important;
  font-size: 11pt !important;
  line-height: 1.6 !important;
  text-align: left !important;
}

.theme-classic :deep(.rendered-markdown h3),
.theme-classic :deep(.rendered-markdown p),
.theme-classic :deep(.rendered-markdown li),
.theme-classic :deep(.rendered-markdown h1),
.theme-classic :deep(.rendered-markdown h2) {
  break-inside: avoid !important;
}

.theme-classic :deep(.rendered-markdown h1) {
  font-size: 26pt !important;
  font-weight: 900 !important;
  text-align: center !important;
  margin-top: 0 !important;
  margin-bottom: 2pt !important;
  color: #000000 !important;
  letter-spacing: -0.04em !important;
  line-height: 1.1 !important;
}

.theme-classic :deep(.rendered-markdown h2) {
  font-size: 14pt !important;
  font-weight: 600 !important;
  text-align: center !important;
  color: #4b5563 !important;
  margin-top: 0 !important;
  margin-bottom: 2pt !important;
}

.theme-classic :deep(.rendered-markdown h2 + p),
.theme-classic :deep(.rendered-markdown > p:nth-of-type(1)) {
  text-align: center !important;
  font-size: 10.5pt !important;
  font-weight: 500 !important;
  color: #4b5563 !important;
  margin-top: 6pt !important;
  margin-bottom: 20pt !important;
}

.theme-classic :deep(.rendered-markdown h3) {
  font-size: 12pt !important;
  font-weight: 800 !important;
  color: #1e3a8a !important; 
  text-transform: uppercase !important;
  letter-spacing: 0.12em !important;
  margin-top: 18pt !important;
  margin-bottom: 10pt !important;
  padding-bottom: 4pt !important;
  border-bottom: 1.5px solid #cbd5e1 !important;
}

.theme-classic :deep(.rendered-markdown p) {
  margin-top: 0 !important;
  margin-bottom: 8pt !important;
  text-align: justify !important;
  color: #1f2937 !important;
}

.theme-classic :deep(.rendered-markdown ul) {
  padding-left: 14pt !important;
  margin-top: 4pt !important;
  margin-bottom: 10pt !important;
  list-style-type: none !important;
}

.theme-classic :deep(.rendered-markdown li) {
  margin-bottom: 3pt !important;
  position: relative !important;
  padding-left: 12pt !important;
  color: #1f2937 !important;
}

.theme-classic :deep(.rendered-markdown li::before) {
  content: '•' !important;
  position: absolute !important;
  left: 0 !important;
  color: #6b7280 !important;
  font-weight: bold !important;
  font-size: 1.2em !important;
  top: 0.1em !important;
}

.theme-classic :deep(.rendered-markdown strong) {
  font-weight: 800 !important;
  color: #000000 !important;
}

.theme-classic :deep(.rendered-markdown em) {
  font-style: italic !important;
  color: #6b7280 !important;
  font-weight: 600 !important;
  font-size: 10.5pt !important;
  float: right !important;
}

.theme-classic :deep(.rendered-markdown hr) { display: none !important; }
.theme-classic :deep(.rendered-markdown p::after) { content: ""; display: block; clear: both; }

/* =========================================
   THEME: TECH (Monospace & Emerald accents)
   ========================================= */
.theme-tech {
  font-family: 'Roboto Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
}

.theme-tech :deep(.rendered-markdown) {
  color: #27272a !important; /* Zinc 800 */
  font-size: 10.5pt !important;
  line-height: 1.6 !important;
  text-align: left !important;
}

.theme-tech :deep(.rendered-markdown h3),
.theme-tech :deep(.rendered-markdown p),
.theme-tech :deep(.rendered-markdown li),
.theme-tech :deep(.rendered-markdown h1),
.theme-tech :deep(.rendered-markdown h2) {
  break-inside: avoid !important;
}

.theme-tech :deep(.rendered-markdown h1) {
  font-size: 24pt !important;
  font-weight: 700 !important;
  text-align: left !important; /* Left aligned for tech */
  margin-top: 0 !important;
  margin-bottom: 4pt !important;
  color: #18181b !important;
  letter-spacing: -0.05em !important;
}

.theme-tech :deep(.rendered-markdown h2) {
  font-size: 13pt !important;
  font-weight: 500 !important;
  text-align: left !important;
  color: #52525b !important;
  margin-top: 0 !important;
  margin-bottom: 2pt !important;
}

/* Contacts line */
.theme-tech :deep(.rendered-markdown h2 + p),
.theme-tech :deep(.rendered-markdown > p:nth-of-type(1)) {
  text-align: left !important;
  font-size: 10pt !important;
  font-weight: 500 !important;
  color: #52525b !important;
  margin-top: 4pt !important;
  margin-bottom: 24pt !important;
  padding-bottom: 8pt !important;
  border-bottom: 1px dashed #d4d4d8 !important;
}

.theme-tech :deep(.rendered-markdown h3) {
  font-size: 13pt !important;
  font-weight: 700 !important;
  color: #059669 !important; /* Emerald 600 */
  text-transform: lowercase !important;
  letter-spacing: 0em !important;
  margin-top: 18pt !important;
  margin-bottom: 8pt !important;
  padding-bottom: 0 !important;
  border-bottom: none !important;
}
.theme-tech :deep(.rendered-markdown h3::before) {
  content: '~/ ' !important;
  color: #a1a1aa !important;
}

.theme-tech :deep(.rendered-markdown p) {
  margin-top: 0 !important;
  margin-bottom: 8pt !important;
  text-align: left !important; /* Never justify in tech */
  color: #3f3f46 !important;
}

.theme-tech :deep(.rendered-markdown ul) {
  padding-left: 12pt !important;
  margin-top: 4pt !important;
  margin-bottom: 10pt !important;
  list-style-type: none !important;
}

.theme-tech :deep(.rendered-markdown li) {
  margin-bottom: 3pt !important;
  position: relative !important;
  padding-left: 14pt !important;
  color: #3f3f46 !important;
}

.theme-tech :deep(.rendered-markdown li::before) {
  content: '>' !important;
  position: absolute !important;
  left: 0 !important;
  color: #10b981 !important;
  font-weight: bold !important;
  font-size: 1.1em !important;
  top: 0 !important;
}

.theme-tech :deep(.rendered-markdown strong) {
  font-weight: 700 !important;
  color: #18181b !important;
  background-color: #f4f4f5 !important;
  padding: 0 2pt !important;
  border-radius: 2px !important;
}

.theme-tech :deep(.rendered-markdown em) {
  font-style: normal !important;
  color: #71717a !important;
  font-weight: 500 !important;
  font-size: 10pt !important;
  float: right !important;
}

.theme-tech :deep(.rendered-markdown hr) { display: none !important; }
.theme-tech :deep(.rendered-markdown p::after) { content: ""; display: block; clear: both; }

</style>
