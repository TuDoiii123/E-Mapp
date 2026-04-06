/**
 * ui.ts — E-Mapp UI utilities
 * Class composition, variant helpers, and design-system constants.
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/* ══════════════════════════════════════════════
   1. Core class-merge utility
   ══════════════════════════════════════════════ */

/** Merges Tailwind classes, resolving conflicts correctly. */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/* ══════════════════════════════════════════════
   2. Design tokens (mirrors globals.css :root)
   ══════════════════════════════════════════════ */

export const tokens = {
  color: {
    primary:            '#8f000d',
    primaryContainer:   '#b22222',
    primaryFixed:       '#ffdad6',
    onPrimary:          '#ffffff',

    secondary:              '#705d00',
    secondaryContainer:     '#fcd400',
    onSecondary:            '#ffffff',
    onSecondaryContainer:   '#6e5c00',

    surface:                  '#f9f9f9',
    surfaceContainerLowest:   '#ffffff',
    surfaceContainerLow:      '#f3f3f3',
    surfaceContainer:         '#eeeeee',
    surfaceContainerHigh:     '#e8e8e8',
    surfaceContainerHighest:  '#e2e2e2',

    onSurface:        '#1a1c1c',
    onSurfaceVariant: '#5a403e',
    outline:          '#8e706d',
    outlineVariant:   '#e2beba',

    error:            '#ba1a1a',
    errorContainer:   '#ffdad6',
    onError:          '#ffffff',
    onErrorContainer: '#93000a',
  },
  font: {
    sans: "'Public Sans', ui-sans-serif, system-ui, sans-serif",
  },
  radius: {
    none: '0',
    sm:   '0.125rem',
    md:   '0.25rem',
    lg:   '0.5rem',
    full: '0.75rem',
  },
  shadow: {
    sm: '0 1px 3px rgba(142, 112, 109, 0.12)',
    md: '0 4px 12px rgba(142, 112, 109, 0.14)',
    lg: '0 12px 40px rgba(142, 112, 109, 0.16)',
  },
} as const;

/* ══════════════════════════════════════════════
   3. Button variants
   ══════════════════════════════════════════════ */

type BtnVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'gold';
type BtnSize    = 'xs' | 'sm' | 'md' | 'lg';

const btnBase =
  'inline-flex items-center justify-center gap-2 font-bold uppercase tracking-widest rounded-sm cursor-pointer transition-all active:scale-[0.97] disabled:opacity-40 disabled:pointer-events-none select-none whitespace-nowrap';

const btnVariants: Record<BtnVariant, string> = {
  primary:  'bg-[#8f000d] text-white shadow-md hover:bg-[#b22222]',
  secondary:'bg-[#fcd400] text-[#6e5c00] hover:brightness-95',
  outline:  'bg-transparent text-[#1a1c1c] border border-[#8e706d] hover:bg-[#f3f3f3]',
  ghost:    'bg-transparent text-[#5a403e] hover:bg-[#f3f3f3]',
  danger:   'bg-[#ba1a1a] text-white hover:bg-[#93000a]',
  gold:     'bg-[#705d00] text-white hover:bg-[#544600]',
};

const btnSizes: Record<BtnSize, string> = {
  xs: 'px-4  py-2   text-[10px]',
  sm: 'px-6  py-2.5 text-xs',
  md: 'px-8  py-3   text-xs',
  lg: 'px-10 py-4   text-sm',
};

export function btn(variant: BtnVariant = 'primary', size: BtnSize = 'md', extra?: ClassValue): string {
  return cn(btnBase, btnVariants[variant], btnSizes[size], extra);
}

/* ══════════════════════════════════════════════
   4. Card variants
   ══════════════════════════════════════════════ */

type CardVariant = 'default' | 'flat' | 'bordered' | 'accentRed' | 'accentGold' | 'elevated';

const cardBase = 'bg-white overflow-hidden rounded-sm';

const cardVariants: Record<CardVariant, string> = {
  default:    'shadow-sm',
  flat:       'bg-[#f3f3f3]',
  bordered:   'border border-[#e2beba]',
  accentRed:  'border-l-4 border-[#8f000d] shadow-sm',
  accentGold: 'border-l-4 border-[#705d00] shadow-sm',
  elevated:   'shadow-[0_12px_40px_rgba(142,112,109,0.16)]',
};

export function card(variant: CardVariant = 'default', extra?: ClassValue): string {
  return cn(cardBase, cardVariants[variant], extra);
}

/* ══════════════════════════════════════════════
   5. Input / label helpers
   ══════════════════════════════════════════════ */

export const cls = {
  /** Field label (10px, bold, uppercase, tracked) */
  label: 'block text-[10px] font-bold text-[#5a403e] uppercase tracking-wider mb-1',

  /** Standard bordered input */
  input: [
    'w-full border border-[#e2beba] bg-white px-3 py-2.5 rounded-sm',
    'text-sm text-[#1a1c1c] placeholder:text-[#8e706d]',
    'outline-none focus:border-[#8f000d] focus:ring-1 focus:ring-[#8f000d] transition-colors',
  ].join(' '),

  /** Underline-only select / input */
  underline: [
    'w-full bg-transparent border-0 border-b-2 border-[#8e706d] py-3',
    'text-sm text-[#1a1c1c] outline-none focus:border-[#705d00] transition-colors',
  ].join(' '),

  /** Section heading with red accent */
  sectionTitle: 'text-lg font-extrabold text-[#1a1c1c] uppercase tracking-tight',

  /** Micro-label used inside summary cards */
  microLabel: 'text-[10px] font-black text-[#5a403e] uppercase tracking-widest',
} as const;

/* ══════════════════════════════════════════════
   6. Badge helpers
   ══════════════════════════════════════════════ */

type BadgeVariant = 'primary' | 'secondary' | 'surface' | 'error' | 'success';

const badgeBase = 'inline-flex items-center px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest rounded-sm';

const badgeVariants: Record<BadgeVariant, string> = {
  primary:   'bg-[#ffdad6] text-[#410003]',
  secondary: 'bg-[#fcd400] text-[#6e5c00]',
  surface:   'bg-[#e8e8e8] text-[#5a403e]',
  error:     'bg-[#ffdad6] text-[#93000a]',
  success:   'bg-emerald-100 text-emerald-800',
};

export function badge(variant: BadgeVariant = 'surface', extra?: ClassValue): string {
  return cn(badgeBase, badgeVariants[variant], extra);
}

/* ══════════════════════════════════════════════
   7. Status helpers
   ══════════════════════════════════════════════ */

export const appointmentStatus = {
  pending: {
    badge: badge('secondary'),
    dot:   'bg-amber-400',
    label: 'Chờ duyệt',
  },
  completed: {
    badge: badge('success'),
    dot:   'bg-emerald-500',
    label: 'Hoàn thành',
  },
  cancelled: {
    badge: badge('error'),
    dot:   'bg-red-500',
    label: 'Đã hủy',
  },
} as const;

export function getStatusConfig(status: string) {
  return appointmentStatus[status as keyof typeof appointmentStatus] ?? appointmentStatus.pending;
}

/* ══════════════════════════════════════════════
   8. Date / time formatters
   ══════════════════════════════════════════════ */

/** Format `YYYY-MM-DD` → `DD/MM/YYYY` */
export function fmtDate(iso: string): string {
  if (!iso) return '—';
  const [y, m, d] = iso.split('-');
  return `${d}/${m}/${y}`;
}

/** Format `YYYY-MM-DD` → `Thứ X, ngày DD/MM/YYYY` */
export function fmtDateLong(iso: string): string {
  if (!iso) return '—';
  const date = new Date(iso + 'T00:00:00');
  const dow = ['Chủ nhật','Thứ Hai','Thứ Ba','Thứ Tư','Thứ Năm','Thứ Sáu','Thứ Bảy'][date.getDay()];
  const [y, m, d] = iso.split('-');
  return `${dow}, ngày ${d}/${m}/${y}`;
}

/** Return today as `YYYY-MM-DD` */
export function todayISO(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

/** Check if a `YYYY-MM-DD` string is in the past */
export function isPastDate(iso: string): boolean {
  return new Date(iso + 'T00:00:00') < new Date(new Date().toDateString());
}

/* ══════════════════════════════════════════════
   9. Calendar builder
   ══════════════════════════════════════════════ */

export interface CalDay { day: number; current: boolean; iso: string }

/** Build a 42-cell (6-row) Monday-first calendar grid */
export function buildCalendarMonth(year: number, month: number): CalDay[] {
  const firstDow = new Date(year, month, 1).getDay();
  const offset   = firstDow === 0 ? 6 : firstDow - 1;
  const dim      = new Date(year, month + 1, 0).getDate();
  const prevDim  = new Date(year, month, 0).getDate();

  const pad = (n: number) => String(n).padStart(2, '0');
  const mm  = pad(month + 1);
  const yy  = String(year);

  const days: CalDay[] = [];
  for (let i = offset - 1; i >= 0; i--) {
    const d   = prevDim - i;
    const pm  = pad(month === 0 ? 12 : month);
    const py  = String(month === 0 ? year - 1 : year);
    days.push({ day: d, current: false, iso: `${py}-${pm}-${pad(d)}` });
  }
  for (let i = 1; i <= dim; i++) {
    days.push({ day: i, current: true, iso: `${yy}-${mm}-${pad(i)}` });
  }
  const rem = 42 - days.length;
  for (let i = 1; i <= rem; i++) {
    const nm  = pad(month === 11 ? 1 : month + 2);
    const ny  = String(month === 11 ? year + 1 : year);
    days.push({ day: i, current: false, iso: `${ny}-${nm}-${pad(i)}` });
  }
  return days;
}

/* ══════════════════════════════════════════════
   10. Confirm-code generator
   ══════════════════════════════════════════════ */

/** Generate a deterministic-ish booking code, e.g. `2403-HN-042` */
export function genConfirmCode(): string {
  const d   = new Date();
  const yr  = d.getFullYear().toString().slice(-2);
  const mo  = String(d.getMonth() + 1).padStart(2, '0');
  const num = String(Math.floor(Math.random() * 900) + 100);
  return `${yr}${mo}-HN-${num}`;
}

/* ══════════════════════════════════════════════
   11. Form validation helpers
   ══════════════════════════════════════════════ */

export const validators = {
  phone:    (v: string) => /^(0[0-9]{9,10})$/.test(v),
  required: (v: string) => v.trim().length > 0,
  minLen:   (v: string, n: number) => v.trim().length >= n,
  futureDateTime: (date: string, time: string) =>
    new Date(`${date}T${time}`) > new Date(),
};

export function validateAppointmentForm(fields: {
  fullName: string; phone: string; date: string; time: string; agencyId: string; serviceCode: string;
}): string[] {
  const errs: string[] = [];
  if (!validators.minLen(fields.fullName, 2))          errs.push('Họ tên phải >= 2 ký tự');
  if (!validators.phone(fields.phone))                  errs.push('Số điện thoại không hợp lệ (0xxxxxxxxx)');
  if (!fields.date)                                     errs.push('Chưa chọn ngày hẹn');
  if (!fields.time)                                     errs.push('Chưa chọn giờ hẹn');
  if (fields.date && fields.time && !validators.futureDateTime(fields.date, fields.time))
                                                        errs.push('Thời gian đã qua, vui lòng chọn lại');
  if (!validators.required(fields.agencyId))            errs.push('Chưa chọn cơ quan');
  if (!validators.required(fields.serviceCode))         errs.push('Chưa chọn dịch vụ');
  return errs;
}
