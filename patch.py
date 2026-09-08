import re

with open('www/index.html', 'r') as f:
    content = f.read()

# 1. Update HTML tags for animated numbers
content = content.replace('x-text="formatRupiah(totalKekayaan)"', 'x-text="formatRupiah(animatedTotalKekayaan)"')
content = content.replace('x-text="formatRupiah(totalPengeluaran)"', 'x-text="formatRupiah(animatedTotalPengeluaran)"')
# Note: targetBudget is not animated

# 2. Inject report modal HTML before Settings Modal
report_modal_html = """  <!-- MODAL "LAPORAN KOMPARATIF" -->
  <div x-show="activeModal === 'report'" style="display: none;" class="fixed inset-0 z-40 bg-slate-50 flex flex-col pt-safe"
       x-transition:enter="transition transform duration-300 ease-[cubic-bezier(0.32,0.72,0,1)]"
       x-transition:enter-start="translate-y-full"
       x-transition:enter-end="translate-y-0"
       x-transition:leave="transition transform duration-200 ease-in"
       x-transition:leave-start="translate-y-0"
       x-transition:leave-end="translate-y-full">
    
    <div class="bg-white px-5 py-4 border-b border-slate-100 flex justify-between items-center shadow-sm z-10 shrink-0">
      <div class="flex items-center">
        <button @click="activeModal = null" class="p-2 -ml-2 mr-2 text-slate-600 bg-slate-100 rounded-full transition-transform active:scale-95 duration-150 ease-out">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"></path></svg>
        </button>
        <h2 class="text-lg font-bold text-slate-800">Laporan Komparatif</h2>
      </div>
      <button @click="exportToPDF()" class="px-3 py-1.5 bg-emerald-600 text-white rounded-lg text-sm font-bold transition-transform active:scale-95 duration-150 ease-out flex items-center shadow-md shadow-emerald-600/30">
        Export PDF
      </button>
    </div>
    
    <div class="bg-white px-5 py-4 border-b border-slate-100 shadow-sm z-0 shrink-0">
      <div class="flex space-x-2 bg-slate-100 p-1 rounded-xl">
        <button @click="reportRange = 3; updateReportChart()" class="flex-1 py-2 text-sm font-bold rounded-lg transition-all active:scale-95 duration-150" :class="reportRange === 3 ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500'">3 Bulan</button>
        <button @click="reportRange = 6; updateReportChart()" class="flex-1 py-2 text-sm font-bold rounded-lg transition-all active:scale-95 duration-150" :class="reportRange === 6 ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500'">6 Bulan</button>
        <button @click="reportRange = 12; updateReportChart()" class="flex-1 py-2 text-sm font-bold rounded-lg transition-all active:scale-95 duration-150" :class="reportRange === 12 ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500'">1 Tahun</button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto px-5 py-6 pb-20">
      <template x-if="transactions.length < 2">
        <div class="text-center py-12">
          <div class="text-5xl mb-4">📊</div>
          <div class="text-slate-600 font-bold text-base mb-1">Belum cukup data buat lihat tren.</div>
          <div class="text-slate-400 text-sm font-medium">Catat transaksi minimal 2 bulan ya.</div>
        </div>
      </template>
      <div x-show="transactions.length >= 2" class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <div class="relative h-64 w-full flex justify-center">
          <canvas id="reportChart"></canvas>
        </div>
      </div>
    </div>
  </div>

  <!-- MODAL: SETTINGS -->"""
content = content.replace('  <!-- MODAL: SETTINGS -->', report_modal_html)

# 3. Add Laporan button to homepage header
header_btn = """      <button @click="activeModal = 'settings'" class="p-2 bg-emerald-700/50 rounded-full transition-transform active:scale-95 duration-150 ease-out">
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
      </button>"""
header_btn_new = """      <div class="flex space-x-2">
        <button @click="activeModal = 'report'; $nextTick(() => updateReportChart());" class="p-2 bg-emerald-700/50 rounded-full transition-transform active:scale-95 duration-150 ease-out">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
        </button>
        <button @click="activeModal = 'settings'" class="p-2 bg-emerald-700/50 rounded-full transition-transform active:scale-95 duration-150 ease-out">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
        </button>
      </div>"""
content = content.replace(header_btn, header_btn_new)

# 4. Staggered list in "all_history"
list_item_start = """        <template x-for="t in filteredTransactions" :key="t.id">
          <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-100 flex items-center justify-between">"""
list_item_new = """        <template x-for="(t, index) in filteredTransactions" :key="t.id">
          <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-100 flex items-center justify-between animate-[toast-in_0.3s_ease-out_forwards]" :style="'animation-delay: ' + Math.min(index * 20, 300) + 'ms; opacity: 0;'">"""
content = content.replace(list_item_start, list_item_new)

with open('www/index.html', 'w') as f:
    f.write(content)
