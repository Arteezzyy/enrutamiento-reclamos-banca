import { ClipboardList, Landmark, Layers, Plus, ShieldCheck } from 'lucide-react'

const NAV = [
  { id: 'clasificar', label: 'Nuevo reclamo', hint: 'Clasificación con IA', icon: Plus },
  { id: 'lista', label: 'Lista de reclamos', hint: 'Historial y seguimiento', icon: ClipboardList },
  { id: 'asignar', label: 'Asignación óptima', hint: 'Optimización ILP', icon: Layers },
]

export default function Sidebar({ activeTab, onChange, reclamos }) {
  return (
    <aside className="relative z-20 flex w-full shrink-0 flex-col overflow-hidden bg-navy text-white lg:sticky lg:top-0 lg:h-screen lg:w-[286px]">
      <div className="pointer-events-none absolute -right-24 -top-24 h-64 w-64 rounded-full bg-accent/25 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-32 -left-16 h-64 w-64 rounded-full bg-gold/10 blur-3xl" />

      <div className="relative flex items-center gap-3 px-5 pb-4 pt-5 lg:px-6 lg:pb-6 lg:pt-7">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-gold to-[#9A7A16] text-navy shadow-lg shadow-black/25">
          <Landmark className="h-6 w-6" strokeWidth={2.2} />
        </div>
        <div className="min-w-0">
          <p className="truncate text-[15px] font-bold leading-tight tracking-tight">Enrutamiento</p>
          <p className="truncate text-xs font-medium text-white/55">Reclamos bancarios</p>
        </div>
        <span className="ml-auto hidden shrink-0 rounded-full border border-white/15 px-2 py-0.5 text-[10px] font-semibold text-white/60 lg:inline">
          v1.0
        </span>
      </div>

      <nav className="no-scrollbar relative flex gap-2 overflow-x-auto border-t border-white/5 px-3 py-3 lg:flex-col lg:gap-1.5 lg:overflow-visible lg:border-t-0 lg:px-4 lg:py-2">
        {NAV.map(({ id, label, hint, icon: Icon }) => {
          const activo = activeTab === id
          return (
            <button
              key={id}
              type="button"
              onClick={() => onChange(id)}
              aria-current={activo ? 'page' : undefined}
              className={`group relative flex shrink-0 items-center gap-3 rounded-xl px-3.5 py-2.5 text-left transition-all duration-200 lg:w-full ${
                activo
                  ? 'bg-white/[0.09] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.07)]'
                  : 'text-white/60 hover:bg-white/[0.05] hover:text-white/90'
              }`}
            >
              <span
                className={`absolute left-0 top-1/2 hidden h-6 w-1 -translate-y-1/2 rounded-r-full bg-accent transition-opacity lg:block ${
                  activo ? 'opacity-100' : 'opacity-0'
                }`}
              />
              <span
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg transition-colors ${
                  activo ? 'bg-accent/15 text-accent' : 'bg-white/5 text-white/50 group-hover:text-white/80'
                }`}
              >
                <Icon className="h-4 w-4" strokeWidth={2.2} />
              </span>
              <span className="min-w-0">
                <span className="block whitespace-nowrap text-sm font-semibold leading-tight">{label}</span>
                <span className="hidden whitespace-nowrap text-[11px] leading-tight text-white/40 lg:block">{hint}</span>
              </span>
            </button>
          )
        })}
      </nav>

      <div className="relative mt-auto hidden px-4 pb-6 pt-4 lg:block">
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
          <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.14em] text-white/45">
            <ShieldCheck className="h-3.5 w-3.5 text-accent" />
            Modelo activo
          </div>
          <p className="mt-2 text-sm font-semibold leading-snug">TF-IDF + Regresión Logística</p>
          <div className="mt-3 grid grid-cols-2 gap-2 text-center">
            <div className="rounded-lg bg-white/5 py-2">
              <p className="text-base font-bold leading-none text-white">{reclamos.length}</p>
              <p className="mt-1 text-[10px] uppercase tracking-wide text-white/45">Reclamos</p>
            </div>
            <div className="rounded-lg bg-white/5 py-2">
              <p className="text-base font-bold leading-none text-white">3</p>
              <p className="mt-1 text-[10px] uppercase tracking-wide text-white/45">Áreas</p>
            </div>
          </div>
        </div>
        <p className="mt-4 px-1 text-[11px] leading-relaxed text-white/35">
          Ingeniería de Sistemas · UMSS
          <br />
          Inteligencia Artificial
        </p>
      </div>
    </aside>
  )
}
