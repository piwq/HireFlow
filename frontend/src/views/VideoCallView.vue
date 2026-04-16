<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Room, RoomEvent, Track } from 'livekit-client'
import api from '@/api/index.js'
import { PhoneOff, Mic, MicOff, Video as VideoIcon, VideoOff, Loader2, Users } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const roomCode = route.params.roomCode

let room = null
const loading = ref(true)
const error = ref('')
const micEnabled = ref(true)
const camEnabled = ref(true)
const localVideoEl = ref(null)
const participants = ref([]) // { identity, name, videoTrack }

// Non-reactive map: identity -> <video> DOM element
const videoEls = {}

function setVideoEl(el, identity) {
  if (el) {
    videoEls[identity] = el
    // If track arrived before DOM (race), attach now
    const p = participants.value.find(p => p.identity === identity)
    if (p?.videoTrack) p.videoTrack.attach(el)
  } else {
    delete videoEls[identity]
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get('/livekit/token', { params: { room: roomCode } })

    // LiveKit URL: same host, port 7880
    const wsProto = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const livekitUrl = `${wsProto}//${location.hostname}:7880`

    room = new Room({ adaptiveStream: true, dynacast: true })

    // Show participant as soon as they connect (even without video)
    room.on(RoomEvent.ParticipantConnected, (participant) => {
      if (!participants.value.find(p => p.identity === participant.identity)) {
        participants.value.push({
          identity: participant.identity,
          name: participant.name || participant.identity,
          videoTrack: null,
        })
      }
    })

    room.on(RoomEvent.TrackSubscribed, (track, _pub, participant) => {
      if (track.kind !== Track.Kind.Video) return
      const existing = participants.value.find(p => p.identity === participant.identity)
      if (existing) {
        existing.videoTrack = track
        const el = videoEls[participant.identity]
        if (el) track.attach(el)
      } else {
        participants.value.push({
          identity: participant.identity,
          name: participant.name || participant.identity,
          videoTrack: track,
        })
      }
    })

    room.on(RoomEvent.TrackUnsubscribed, (track, _pub, participant) => {
      if (track.kind !== Track.Kind.Video) return
      track.detach()
      const p = participants.value.find(p => p.identity === participant.identity)
      if (p) p.videoTrack = null
    })

    room.on(RoomEvent.ParticipantDisconnected, (participant) => {
      participants.value = participants.value.filter(p => p.identity !== participant.identity)
    })

    await room.connect(livekitUrl, data.token)

    // Camera/mic: non-fatal — if it fails, stay in room with cam/mic off
    try {
      await room.localParticipant.enableCameraAndMicrophone()
    } catch (mediaErr) {
      console.warn('[LiveKit] Camera/mic unavailable:', mediaErr.message)
      camEnabled.value = false
      micEnabled.value = false
    }

    // Handle participants who joined before us
    for (const participant of room.remoteParticipants.values()) {
      if (participants.value.find(p => p.identity === participant.identity)) continue
      let videoTrack = null
      for (const pub of participant.videoTrackPublications.values()) {
        if (pub.isSubscribed && pub.track) { videoTrack = pub.track; break }
      }
      participants.value.push({
        identity: participant.identity,
        name: participant.name || participant.identity,
        videoTrack,
      })
    }

    loading.value = false

    // Attach local video AFTER loading=false so <video> element is in the DOM
    nextTick(() => {
      const localTrack = room.localParticipant.getTrackPublication(Track.Source.Camera)?.track
      if (localTrack && localVideoEl.value) localTrack.attach(localVideoEl.value)
    })
  } catch (e) {
    console.error('[LiveKit]', e)
    error.value = e.message || 'Ошибка подключения к комнате'
    loading.value = false
  }
})

onUnmounted(() => room?.disconnect())

async function toggleMic() {
  await room?.localParticipant.setMicrophoneEnabled(!micEnabled.value)
  micEnabled.value = !micEnabled.value
}

async function toggleCam() {
  await room?.localParticipant.setCameraEnabled(!camEnabled.value)
  camEnabled.value = !camEnabled.value
}

function leave() {
  room?.disconnect()
  router.back()
}
</script>

<template>
  <div class="fixed inset-0 bg-[#0d0f1a] flex flex-col z-50">
    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-3 bg-brand-dark-surface border-b border-brand-dark-border shrink-0">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-brand-accent flex items-center justify-center">
          <VideoIcon class="w-4 h-4 text-white" />
        </div>
        <span class="font-bold text-brand-dark-primary text-sm">HireFlow</span>
        <span class="text-brand-dark-secondary text-caption">Видеозвонок</span>
        <span class="text-micro text-brand-dark-muted font-mono bg-brand-dark-elevated px-2 py-0.5 rounded">{{ roomCode }}</span>
      </div>
      <button
        @click="leave"
        class="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-xl text-sm font-bold transition-all active:scale-95"
      >
        <PhoneOff class="w-4 h-4" />
        Завершить
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex-1 flex flex-col items-center justify-center gap-4">
      <Loader2 class="w-12 h-12 animate-spin text-brand-accent" />
      <p class="text-brand-dark-secondary">Подключение к комнате...</p>
      <p class="text-brand-dark-muted text-caption font-mono">{{ roomCode }}</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="flex-1 flex flex-col items-center justify-center gap-4 text-center px-8">
      <div class="w-16 h-16 rounded-2xl bg-red-500/10 flex items-center justify-center">
        <PhoneOff class="w-8 h-8 text-red-500" />
      </div>
      <p class="text-white font-semibold">{{ error }}</p>
      <button @click="router.back()" class="px-6 py-2.5 border border-brand-dark-border rounded-xl text-brand-dark-secondary text-sm hover:bg-brand-dark-elevated transition-colors">
        Вернуться назад
      </button>
    </div>

    <!-- Video grid -->
    <div v-else class="flex-1 flex flex-col overflow-hidden">
      <div
        class="flex-1 p-4 grid gap-3 overflow-hidden"
        :class="{
          'grid-cols-1': participants.length === 0,
          'grid-cols-2': participants.length >= 1,
        }"
      >
        <!-- Local video -->
        <div class="relative bg-brand-dark-elevated rounded-2xl overflow-hidden flex items-center justify-center min-h-0">
          <video ref="localVideoEl" autoplay muted playsinline class="w-full h-full object-cover" />
          <div v-if="!camEnabled" class="absolute inset-0 bg-brand-dark-elevated flex items-center justify-center">
            <VideoOff class="w-12 h-12 text-brand-dark-muted" />
          </div>
          <div class="absolute bottom-3 left-3 bg-black/60 backdrop-blur-sm px-2.5 py-1 rounded-lg text-white text-xs font-medium flex items-center gap-1.5">
            <span>Вы</span>
            <MicOff v-if="!micEnabled" class="w-3 h-3 text-red-400" />
          </div>
        </div>

        <!-- Remote participants -->
        <div
          v-for="p in participants"
          :key="p.identity"
          class="relative bg-brand-dark-elevated rounded-2xl overflow-hidden flex items-center justify-center min-h-0"
        >
          <video
            :ref="el => setVideoEl(el, p.identity)"
            autoplay
            playsinline
            class="w-full h-full object-cover"
          />
          <div v-if="!p.videoTrack" class="absolute inset-0 flex flex-col items-center justify-center gap-3">
            <div class="w-16 h-16 rounded-full bg-brand-accent/20 border border-brand-accent/30 flex items-center justify-center">
              <span class="text-white text-2xl font-bold">{{ (p.name || '?')[0].toUpperCase() }}</span>
            </div>
            <p class="text-brand-dark-secondary text-sm">{{ p.name }}</p>
          </div>
          <div class="absolute bottom-3 left-3 bg-black/60 backdrop-blur-sm px-2.5 py-1 rounded-lg text-white text-xs font-medium">
            {{ p.name }}
          </div>
        </div>

        <!-- Waiting placeholder (only shown when no remote participants) -->
        <div
          v-if="participants.length === 0"
          class="bg-brand-dark-elevated/50 rounded-2xl border-2 border-dashed border-brand-dark-border flex flex-col items-center justify-center gap-3"
        >
          <Users class="w-12 h-12 text-brand-dark-muted" />
          <p class="text-brand-dark-secondary text-sm">Ожидание участников...</p>
        </div>
      </div>

      <!-- Controls -->
      <div class="py-5 flex items-center justify-center gap-4 shrink-0">
        <button
          @click="toggleMic"
          :title="micEnabled ? 'Выключить микрофон' : 'Включить микрофон'"
          class="w-13 h-13 rounded-full flex items-center justify-center transition-all active:scale-95"
          :class="micEnabled
            ? 'bg-brand-dark-elevated hover:bg-brand-dark-border text-white w-12 h-12'
            : 'bg-red-500/20 hover:bg-red-500/30 text-red-400 w-12 h-12'"
        >
          <component :is="micEnabled ? Mic : MicOff" class="w-5 h-5" />
        </button>

        <button
          @click="toggleCam"
          :title="camEnabled ? 'Выключить камеру' : 'Включить камеру'"
          class="w-12 h-12 rounded-full flex items-center justify-center transition-all active:scale-95"
          :class="camEnabled
            ? 'bg-brand-dark-elevated hover:bg-brand-dark-border text-white'
            : 'bg-red-500/20 hover:bg-red-500/30 text-red-400'"
        >
          <component :is="camEnabled ? VideoIcon : VideoOff" class="w-5 h-5" />
        </button>

        <button
          @click="leave"
          class="w-14 h-14 rounded-full bg-red-500 hover:bg-red-600 flex items-center justify-center text-white transition-all shadow-lg shadow-red-500/30 active:scale-95"
        >
          <PhoneOff class="w-6 h-6" />
        </button>
      </div>
    </div>
  </div>
</template>
