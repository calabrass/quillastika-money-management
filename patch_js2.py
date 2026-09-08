with open('www/index.html', 'r') as f:
    content = f.read()

# 1. State
js_state = """        form: { title: '', amount: '', type: 'keluar', category: 'Umum', date: '', note: '' },
        chartInstance: null,
        reportChartInstance: null,
        reportRange: 6,
        animatedTotalKekayaan: 0,
        animatedTotalPemasukan: 0,
        animatedTotalPengeluaran: 0,"""
content = content.replace("        form: { title: '', amount: '', type: 'keluar', category: 'Umum', date: '', note: '' },\n        chartInstance: null,", js_state)

# 2. Init
js_init = """        init() {
          const saved = localStorage.getItem('quill_transactions');
          this.transactions = saved ? JSON.parse(saved) : [];
          const savedBudget = localStorage.getItem('quill_target_budget');
          if (savedBudget) this.targetBudget = Number(savedBudget);
          
          this.animatedTotalKekayaan = this.totalKekayaan;
          this.animatedTotalPemasukan = this.totalPemasukan;
          this.animatedTotalPengeluaran = this.totalPengeluaran;

          this.$watch('transactions', () => {
              this.animateNumber('animatedTotalKekayaan', this.totalKekayaan);
              this.animateNumber('animatedTotalPemasukan', this.totalPemasukan);
              this.animateNumber('animatedTotalPengeluaran', this.totalPengeluaran);
              if (this.reportChartInstance) this.updateReportChart();
          });

          this.$nextTick(() => {"""
content = content.replace("""        init() {
          const saved = localStorage.getItem('quill_transactions');
          this.transactions = saved ? JSON.parse(saved) : [];
          const savedBudget = localStorage.getItem('quill_target_budget');
          if (savedBudget) this.targetBudget = Number(savedBudget);
          
          this.$nextTick(() => {""", js_init)

# 3. New Methods
js_methods = """        getProgressBarColor() {
            const p = this.budgetPercentage;
            if (p < 60) return 'bg-emerald-500';
            if (p <= 85) return 'bg-amber-500';
            return 'bg-rose-500';
        },

        animateNumber(prop, to) {
            if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                this[prop] = to;
                return;
            }
            let from = this[prop] || 0;
            let duration = 600;
            let start = null;
            const step = (timestamp) => {
                if (!start) start = timestamp;
                let progress = timestamp - start;
                let percentage = Math.min(progress / duration, 1);
                let ease = percentage === 1 ? 1 : 1 - Math.pow(2, -10 * percentage);
                this[prop] = from + (to - from) * ease;
                if (percentage < 1) window.requestAnimationFrame(step);
            };
            window.requestAnimationFrame(step);
        },

        aggregateByMonth(rangeInMonths) {
            const result = [];
            const now = new Date();
            for (let i = rangeInMonths - 1; i >= 0; i--) {
                const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
                const monthKey = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
                const label = d.toLocaleString('id-ID', { month: 'short' }) + (i===rangeInMonths-1 || d.getMonth()===0 ? ` '${String(d.getFullYear()).slice(2)}` : '');
                result.push({ month: monthKey, label, income: 0, expense: 0, investment: 0 });
            }
            this.transactions.forEach(t => {
                const [y, m] = t.date.split('-');
                const monthKey = `${y}-${m}`;
                const bucket = result.find(b => b.month === monthKey);
                if (bucket) {
                    if (t.type === 'masuk') bucket.income += Number(t.amount);
                    else if (t.type === 'keluar') bucket.expense += Number(t.amount);
                    else if (t.type === 'invest') bucket.investment += Number(t.amount);
                }
            });
            return result;
        },

        updateReportChart() {
            const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            if (!this.reportChartInstance) {
                const ctx = document.getElementById('reportChart');
                if (!ctx) return;
                this.reportChartInstance = new Chart(ctx, {
                    type: 'bar',
                    data: this.getReportChartData(),
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: reduceMotion ? false : { duration: 800, easing: 'easeOutQuart' },
                        scales: { x: { stacked: false }, y: { stacked: false, beginAtZero: true } },
                        plugins: { legend: { position: 'bottom' } }
                    }
                });
            } else {
                this.reportChartInstance.options.animation = reduceMotion ? false : { duration: 800, easing: 'easeOutQuart' };
                this.reportChartInstance.data = this.getReportChartData();
                this.reportChartInstance.update();
            }
        },

        getReportChartData() {
            const data = this.aggregateByMonth(this.reportRange);
            return {
                labels: data.map(d => d.label),
                datasets: [
                    { label: 'Pengeluaran', data: data.map(d => d.expense), backgroundColor: '#f43f5e', borderRadius: 4 },
                    { label: 'Pemasukan', data: data.map(d => d.income), backgroundColor: '#10b981', borderRadius: 4 },
                    { label: 'Investasi', data: data.map(d => d.investment), backgroundColor: '#3b82f6', borderRadius: 4 }
                ]
            };
        },

        async saveFileLocally(filename, data, isBase64) {
            const isNative = window.Capacitor && window.Capacitor.isNativePlatform();
            if (isNative && window.Capacitor.Plugins.Filesystem) {
                try {
                    await window.Capacitor.Plugins.Filesystem.writeFile({
                        path: `Download/${filename}`,
                        data: data,
                        directory: 'EXTERNAL_STORAGE',
                        recursive: true
                    });
                    this.showToast(`Tersimpan di Download/${filename}`, 'success');
                    return;
                } catch (e) {
                    console.warn('Fallback to Documents/ due to Scoped Storage:', e);
                    try {
                        await window.Capacitor.Plugins.Filesystem.writeFile({
                            path: filename,
                            data: data,
                            directory: 'DOCUMENTS',
                            recursive: true
                        });
                        this.showToast(`Tersimpan di Documents/${filename}`, 'success');
                        return;
                    } catch(e2) {
                        console.error('File write error:', e2);
                    }
                }
            }
            
            // Web fallback
            let blob;
            if (isBase64) {
                const byteCharacters = atob(data);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) byteNumbers[i] = byteCharacters.charCodeAt(i);
                blob = new Blob([new Uint8Array(byteNumbers)], {type: filename.endsWith('.pdf') ? 'application/pdf' : 'text/csv'});
            } else {
                blob = new Blob([data], { type: 'text/csv;charset=utf-8;' });
            }
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url; link.download = filename; link.style.display = 'none';
            document.body.appendChild(link);
            try { link.click(); } catch(e) {}
            document.body.removeChild(link);
            setTimeout(() => URL.revokeObjectURL(url), 5000);
            this.showToast(`Berhasil mengekspor ${filename}`, 'success');
        },

        exportToPDF() {
            if (!window.jspdf) {
                this.showToast('Library PDF belum siap.', 'error'); return;
            }
            if (this.transactions.length === 0) return this.showToast('Belum ada data.', 'error');
            
            this.showToast('Menyiapkan PDF...', 'success', 1000);
            
            setTimeout(() => {
                try {
                    const doc = new window.jspdf.jsPDF();
                    doc.setFont("helvetica", "bold");
                    doc.setFontSize(20);
                    doc.text("Laporan Keuangan Quill", 14, 22);
                    doc.setFontSize(10);
                    doc.setFont("helvetica", "normal");
                    doc.text(`Tanggal Export: ${new Date().toLocaleDateString('id-ID')}`, 14, 30);
                    
                    if (this.reportChartInstance) {
                        const imgData = this.reportChartInstance.toBase64Image();
                        doc.addImage(imgData, 'PNG', 14, 35, 180, 80);
                    }
                    
                    const body = this.transactions.map(t => [t.date, t.title, t.type.toUpperCase(), this.formatRupiah(t.amount)]);
                    doc.autoTable({
                        startY: this.reportChartInstance ? 120 : 40,
                        head: [['Tanggal', 'Transaksi', 'Tipe', 'Jumlah']],
                        body: body,
                        theme: 'striped',
                        headStyles: { fillColor: [5, 150, 105] }
                    });
                    
                    const dataUri = doc.output('datauristring');
                    const base64Data = dataUri.split(',')[1];
                    const filename = `Quill_Laporan_${new Date().toISOString().slice(0,10)}.pdf`;
                    
                    this.saveFileLocally(filename, base64Data, true);
                } catch(e) {
                    console.error(e);
                    this.showToast('Gagal membuat PDF', 'error');
                }
            }, 100);
        }"""
content = content.replace("""        getProgressBarColor() {
            const p = this.budgetPercentage;
            if (p < 60) return 'bg-emerald-500';
            if (p <= 85) return 'bg-amber-500';
            return 'bg-rose-500';
        }""", js_methods)

# 4. Chart animation fix
chart_animation_fix = """            this.chartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: this.getChartData(),
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? false : { duration: 800, easing: 'easeOutQuart' },
                    cutout: '72%',"""
content = content.replace("""            this.chartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: this.getChartData(),
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '72%',""", chart_animation_fix)

# Write back
with open('www/index.html', 'w') as f:
    f.write(content)
