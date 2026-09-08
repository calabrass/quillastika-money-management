(function (global) {
  'use strict';

  var PINE = [11, 122, 99];
  var PINE_DARK = [7, 92, 75];
  var INK = [23, 33, 29];
  var MUTED = [110, 119, 115];
  var LINE = [228, 232, 230];
  var CREAM = [244, 247, 245];
  var TYPE_COLORS = { masuk: [21, 149, 112], keluar: [214, 69, 82], invest: [74, 127, 193] };
  var TYPE_LABELS = { masuk: 'Pemasukan', keluar: 'Pengeluaran', invest: 'Investasi' };
  var VALID_TYPES = ['masuk', 'keluar', 'invest'];

  function PdfError(code, message) {
    this.name = 'PdfError';
    this.code = code;
    this.message = message || code;
    if (Error.captureStackTrace) Error.captureStackTrace(this, PdfError);
  }
  PdfError.prototype = Object.create(Error.prototype);
  PdfError.prototype.constructor = PdfError;

  function defaultRupiah(val) {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(Number(val) || 0);
  }

  function formatShortDate(dateStr) {
    if (!dateStr || typeof dateStr !== 'string') return '—';
    var d = new Date(dateStr + 'T00:00:00');
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  function sanitizeTransactions(list) {
    return (Array.isArray(list) ? list : [])
      .filter(function (t) {
        return t && typeof t === 'object'
          && VALID_TYPES.indexOf(t.type) !== -1
          && isFinite(Number(t.amount)) && Number(t.amount) > 0;
      })
      .map(function (t) {
        return {
          date: typeof t.date === 'string' ? t.date : '',
          title: typeof t.title === 'string' && t.title.trim() ? t.title.trim() : 'Tanpa judul',
          category: typeof t.category === 'string' && t.category.trim() ? t.category.trim() : 'Umum',
          type: t.type,
          amount: Number(t.amount),
          note: typeof t.note === 'string' ? t.note.trim() : ''
        };
      })
      .sort(function (a, b) { return (a.date || '').localeCompare(b.date || ''); });
  }

  function sumBy(list, type) {
    return list.filter(function (t) { return t.type === type; })
      .reduce(function (s, t) { return s + t.amount; }, 0);
  }

  function breakdownByCategory(list, type) {
    var map = {};
    list.filter(function (t) { return t.type === type; }).forEach(function (t) {
      if (!map[t.category]) map[t.category] = { name: t.category, total: 0, count: 0 };
      map[t.category].total += t.amount;
      map[t.category].count += 1;
    });
    return Object.keys(map).map(function (k) { return map[k]; })
      .sort(function (a, b) { return b.total - a.total; });
  }

  function baseTableStyle() {
    return {
      theme: 'grid',
      styles: { font: 'helvetica', fontSize: 9, textColor: INK, cellPadding: 3, lineColor: LINE, lineWidth: 0.2 },
      headStyles: { fillColor: PINE, textColor: [255, 255, 255], fontStyle: 'bold', fontSize: 9 },
      alternateRowStyles: { fillColor: CREAM }
    };
  }

  function extend(target, source) {
    var out = {};
    Object.keys(target).forEach(function (k) { out[k] = target[k]; });
    Object.keys(source).forEach(function (k) { out[k] = source[k]; });
    return out;
  }

  function exportFinancialReport(options) {
    var opts = options || {};
    var NS = global.window && global.window.jspdf;
    if (!NS || typeof NS.jsPDF !== 'function') {
      throw new PdfError('LIB_MISSING', 'jsPDF library is not loaded.');
    }
    var txs = sanitizeTransactions(opts.transactions);
    if (txs.length === 0) {
      throw new PdfError('NO_DATA', 'No valid transactions to export.');
    }
    var rupiah = typeof opts.formatRupiah === 'function' ? opts.formatRupiah : defaultRupiah;
    var periodLabel = typeof opts.periodLabel === 'string' && opts.periodLabel ? opts.periodLabel : 'Semua periode';
    var exportedOn = new Date().toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' });

    var income = sumBy(txs, 'masuk');
    var expense = sumBy(txs, 'keluar');
    var investment = sumBy(txs, 'invest');
    var net = income - expense;

    var doc = new NS.jsPDF({ unit: 'mm', format: 'a4' });
    var pageW = doc.internal.pageSize.getWidth();
    var margin = 14;
    var contentW = pageW - margin * 2;

    doc.setFillColor(PINE[0], PINE[1], PINE[2]);
    doc.rect(0, 0, pageW, 40, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(22);
    doc.text('QUILLASTIKA', margin, 16);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(11);
    doc.text('Financial Report  ·  ' + periodLabel, margin, 24);
    doc.setFontSize(9);
    doc.text('Tanggal export: ' + exportedOn, margin, 31);

    var y = 48;
    doc.setTextColor(MUTED[0], MUTED[1], MUTED[2]);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(10);
    doc.text('RINGKASAN', margin, y);
    y += 3;

    doc.autoTable(extend(baseTableStyle(), {
      startY: y,
      head: [['Total Pemasukan', 'Total Pengeluaran', 'Saldo Bersih']],
      body: [[rupiah(income), rupiah(expense), rupiah(net)]],
      columnStyles: { 0: { halign: 'left' }, 1: { halign: 'left' }, 2: { halign: 'left', fontStyle: 'bold', textColor: net >= 0 ? PINE_DARK : TYPE_COLORS.keluar } }
    }));
    y = doc.lastAutoTable.finalY + 3;
    doc.setTextColor(MUTED[0], MUTED[1], MUTED[2]);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.text('Total Investasi: ' + rupiah(investment) + '   ·   ' + txs.length + ' transaksi', margin, y);
    y += 8;

    if (opts.chartImage && typeof opts.chartImage === 'string' && opts.chartImage.indexOf('data:image') === 0) {
      try {
        doc.setTextColor(MUTED[0], MUTED[1], MUTED[2]);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(10);
        doc.text('TREN', margin, y);
        doc.addImage(opts.chartImage, 'PNG', margin, y + 3, contentW, 72);
        y += 82;
      } catch (chartErr) {
        y += 2;
      }
    }

    var expenseRows = breakdownByCategory(txs, 'keluar');
    if (expenseRows.length > 0) {
      doc.setTextColor(MUTED[0], MUTED[1], MUTED[2]);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(10);
      doc.text('RINCIAN PENGELUARAN', margin, y);
      y += 3;
      doc.autoTable(extend(baseTableStyle(), {
        startY: y,
        head: [['Kategori', 'Transaksi', 'Jumlah']],
        body: expenseRows.map(function (r) { return [r.name, String(r.count), rupiah(r.total)]; }),
        foot: [['Total', '', rupiah(expense)]],
        footStyles: { fillColor: CREAM, textColor: INK, fontStyle: 'bold' },
        columnStyles: { 0: { cellWidth: 90 }, 1: { halign: 'center', cellWidth: 30 }, 2: { halign: 'right' } }
      }));
      y = doc.lastAutoTable.finalY + 8;
    }

    var incomeRows = breakdownByCategory(txs, 'masuk');
    if (incomeRows.length > 0) {
      if (y > 245) { doc.addPage(); y = 20; }
      doc.setTextColor(MUTED[0], MUTED[1], MUTED[2]);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(10);
      doc.text('RINCIAN PEMASUKAN', margin, y);
      y += 3;
      doc.autoTable(extend(baseTableStyle(), {
        startY: y,
        head: [['Kategori', 'Transaksi', 'Jumlah']],
        body: incomeRows.map(function (r) { return [r.name, String(r.count), rupiah(r.total)]; }),
        foot: [['Total', '', rupiah(income)]],
        footStyles: { fillColor: CREAM, textColor: INK, fontStyle: 'bold' },
        columnStyles: { 0: { cellWidth: 90 }, 1: { halign: 'center', cellWidth: 30 }, 2: { halign: 'right' } }
      }));
      y = doc.lastAutoTable.finalY + 8;
    }

    if (y > 245) { doc.addPage(); y = 20; }
    doc.setTextColor(MUTED[0], MUTED[1], MUTED[2]);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(10);
    doc.text('DAFTAR TRANSAKSI', margin, y);
    y += 3;

    var typeOfRow = txs.map(function (t) { return t.type; });
    doc.autoTable(extend(baseTableStyle(), {
      startY: y,
      head: [['Tanggal', 'Deskripsi', 'Kategori', 'Tipe', 'Jumlah']],
      body: txs.map(function (t) {
        return [formatShortDate(t.date), t.title + (t.note ? '\n' + t.note : ''), t.category, TYPE_LABELS[t.type], rupiah(t.amount)];
      }),
      columnStyles: {
        0: { cellWidth: 24 },
        1: { cellWidth: 'auto' },
        2: { cellWidth: 30 },
        3: { cellWidth: 26 },
        4: { halign: 'right', cellWidth: 32 }
      },
      didParseCell: function (data) {
        if (data.section === 'body' && data.column.index === 3) {
          var c = TYPE_COLORS[typeOfRow[data.row.index]] || INK;
          data.cell.styles.textColor = c;
          data.cell.styles.fontStyle = 'bold';
        }
      },
      didDrawPage: function (data) {
        var pageCount = doc.internal.getNumberOfPages();
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8);
        doc.setTextColor(MUTED[0], MUTED[1], MUTED[2]);
        doc.text('Dibuat dengan Quillastika · Offline', margin, doc.internal.pageSize.getHeight() - 10);
        doc.text('Halaman ' + data.pageNumber + ' dari ' + pageCount, pageW - margin, doc.internal.pageSize.getHeight() - 10, { align: 'right' });
      }
    }));

    var stamp = new Date().toISOString().slice(0, 10);
    var base64 = doc.output('datauristring').split(',')[1];
    return { filename: 'Quillastika_Laporan_' + stamp + '.pdf', base64: base64 };
  }

  global.QuillPDF = {
    exportFinancialReport: exportFinancialReport,
    PdfError: PdfError
  };
})(typeof window !== 'undefined' ? window : this);
