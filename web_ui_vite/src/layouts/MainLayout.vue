<template>
  <!-- Root container: Full screen, flex column, overflow hidden -->
  <div class="h-screen w-screen flex flex-col overflow-hidden m-0 p-0 bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.12),_transparent_34%),linear-gradient(180deg,_#040816,_#0b1220_38%,_#020617)]">
    <!-- Header: Fixed height with tech-style design -->
    <header class="h-14 flex-shrink-0 bg-[linear-gradient(90deg,_rgba(2,6,23,0.98),_rgba(8,47,73,0.92),_rgba(2,6,23,0.98))] flex items-center justify-between px-6 border-b border-cyan-500/30 relative overflow-hidden shadow-[0_0_30px_rgba(8,145,178,0.15)]">
      <!-- Decorative tech elements -->
      <div class="absolute inset-0 opacity-10">
        <div class="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-cyan-400 to-transparent"></div>
        <div class="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-cyan-400 to-transparent"></div>
        <div class="absolute top-0 left-1/4 w-px h-full bg-gradient-to-b from-transparent via-cyan-400 to-transparent"></div>
        <div class="absolute top-0 right-1/4 w-px h-full bg-gradient-to-b from-transparent via-cyan-400 to-transparent"></div>
      </div>

      <!-- Left: Title with glow effect -->
      <div class="flex items-center gap-3 relative z-10">
        <div class="w-8 h-8 rounded bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/50">
          <span class="text-white text-sm font-bold">AI</span>
        </div>
        <h1 class="text-white font-bold text-lg m-0 tracking-wide" style="text-shadow: 0 0 20px rgba(34, 211, 238, 0.5);">
          绝缘子缺陷检测系统
        </h1>
      </div>

      <!-- Right: Settings button -->
      <div class="relative z-10">
        <button
          @click="$emit('open-settings')"
          class="w-10 h-10 flex items-center justify-center text-cyan-400 border border-cyan-500/50 rounded-lg transition-all duration-300 hover:bg-cyan-500/20 hover:shadow-lg hover:shadow-cyan-500/30 hover:border-cyan-400 hover:rotate-90 animate-pulse-slow relative overflow-hidden group"
          title="设置"
        >
          <span class="text-xl relative z-10">⚙</span>
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent -translate-x-full group-hover:animate-shimmer"></div>
        </button>
      </div>
    </header>

    <!-- Main Content: Flex row, fills remaining space -->
    <main class="flex-1 flex overflow-hidden relative">

      <!-- Left Panel: Fixed width (64 * 4 = 256px) -->
      <aside class="w-64 flex-shrink-0 bg-slate-900/70 backdrop-blur border-r border-cyan-500/20 flex flex-col relative z-10 shadow-[inset_-1px_0_0_rgba(34,211,238,0.08)]">
        <!-- Panel Title with tech style -->
        <div class="px-4 py-3 text-sm font-semibold text-cyan-400 border-b border-cyan-500/20 flex-shrink-0 bg-gradient-to-r from-cyan-950/50 to-transparent flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
          <span>记录中心</span>
        </div>

        <!-- Panel Content Slot -->
        <div class="flex-1 overflow-hidden flex flex-col">
          <slot name="left-panel"></slot>
        </div>
      </aside>

      <!-- Center Panel: Fills remaining space (flex-1 + min-w-0) -->
      <section class="flex-1 min-w-0 bg-slate-950/20 flex flex-col relative overflow-hidden z-10">
        <!-- Corner decorations -->
        <div class="absolute top-0 left-0 w-16 h-16 border-t-2 border-l-2 border-cyan-500/30 rounded-tl-lg"></div>
        <div class="absolute top-0 right-0 w-16 h-16 border-t-2 border-r-2 border-cyan-500/30 rounded-tr-lg"></div>
        <div class="absolute bottom-0 left-0 w-16 h-16 border-b-2 border-l-2 border-cyan-500/30 rounded-bl-lg"></div>
        <div class="absolute bottom-0 right-0 w-16 h-16 border-b-2 border-r-2 border-cyan-500/30 rounded-br-lg"></div>

        <!-- Center Content Slot -->
        <slot name="center-panel"></slot>
      </section>

      <!-- Right Panel: Fixed width (80 * 4 = 320px) -->
      <aside class="w-80 flex-shrink-0 bg-slate-900/72 backdrop-blur border-l border-cyan-500/20 flex flex-col overflow-hidden relative z-10 shadow-[inset_1px_0_0_rgba(34,211,238,0.08)]">
        <!-- Panel Title with tech style -->
        <div class="px-4 py-3 text-sm font-semibold text-cyan-400 border-b border-cyan-500/20 flex-shrink-0 bg-gradient-to-r from-cyan-950/50 to-transparent flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
          <span>任务面板</span>
        </div>

        <!-- Panel Content Slot -->
        <div class="flex-1 overflow-hidden flex flex-col">
          <slot name="right-panel"></slot>
        </div>
      </aside>
    </main>
  </div>
</template>

<script setup>
defineEmits(['open-settings'])
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

.animate-pulse-slow {
  animation: pulse-slow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.group:hover .animate-shimmer {
  animation: shimmer 1.5s infinite;
}
</style>
