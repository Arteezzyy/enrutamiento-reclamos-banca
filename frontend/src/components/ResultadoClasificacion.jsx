import { ArrowRight, Sparkles } from 'lucide-react'
import {
  SLA_POR_PRIORIDAD,
  areaMeta,
  porcentaje,
  prioridadMeta,
} from '../lib/ui.js'

export default function ResultadoClasificacion({ resultado, onVerHistorial }) {
  if (!resultado) return null

  const area = areaMeta(resultado.area)
  const prioridad = prioridadMeta(resultado.prioridad)
  const probabilidadesArea = Object.entries(resultado.probabilidades_area ?? {})
    .map(([nombre, valor]) => ({ ...areaMeta(nombre), valor }))
    .sort((a, b) => b.valor - a.valor)
  const probabilidadesPrioridad = Object.entries(resultado.probabilidades_prioridad ?? {}).sort(
    (a, b) => b[1] - a[1],
  )

  return (
    <section className="card animate-fade-up overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-6 py-4">
        <div className="flex items-center gap-2 text-sm font-bold text-navy">
          <Sparkles className="h-4 w-4 text-gold" />
          Resultado de la clasificación
        </div>
        <button
          type="button"
          onClick={onVerHistorial}
          className="inline-flex items-center gap-1 text-xs font-semibold text-accent transition-colors hover:text-accent-dark"
        >
          Ver historial
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </div>

      <div className="grid gap-4 p-6 sm:grid-cols-2">
        <div className={`rounded-xl p-4 ${area.tono.soft}`}>
          <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-muted/80">Área detectada</p>
          <div className="mt-2 flex items-center gap-2.5">
            <span className={`h-2.5 w-2.5 rounded-full ${area.tono.dot}`} />
            <p className={`text-base font-bold leading-tight ${area.tono.text}`}>{area.label}</p>
          </div>
          <p className="mt-2 text-xs text-muted">Destino sugerido para el enrutamiento</p>
        </div>

        <div className="rounded-xl border border-line p-4">
          <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-muted/80">Prioridad</p>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span className={`badge ${prioridad.pill}`}>
              <span className={`h-1.5 w-1.5 rounded-full ${prioridad.dot}`} />
              {prioridad.label}
            </span>
            <span className="text-xs text-muted">
              SLA objetivo: <span className="font-semibold text-ink">{SLA_POR_PRIORIDAD[prioridad.key]} h</span>
            </span>
          </div>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {probabilidadesPrioridad.map(([nombre, valor]) => {
              const meta = prioridadMeta(nombre)
              return (
                <span
                  key={nombre}
                  className={`inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[10px] font-semibold ${meta.pill}`}
                >
                  {meta.label}
                  <span className="tabular-nums opacity-70">{porcentaje(valor)}</span>
                </span>
              )
            })}
          </div>
        </div>
      </div>

      {probabilidadesArea.length > 0 && (
        <div className="border-t border-line px-6 py-5">
          <div className="flex items-center justify-between">
            <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-muted/80">Confianza por área</p>
            <span className="text-[11px] text-muted/70">probabilidad del modelo</span>
          </div>
          <div className="mt-3 space-y-2.5">
            {probabilidadesArea.map((item) => (
              <div key={item.key} className="flex items-center gap-3">
                <span className="w-52 shrink-0 truncate text-xs font-medium text-ink" title={item.label}>
                  {item.label}
                </span>
                <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-line">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${item.tono.bar}`}
                    style={{ width: `${Math.max(item.valor * 100, 1.5)}%` }}
                  />
                </div>
                <span className="w-10 shrink-0 text-right text-xs font-semibold tabular-nums text-muted">
                  {porcentaje(item.valor)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex items-center gap-2 border-t border-line bg-[#FAFBFD] px-6 py-3 text-xs text-muted">
        <span className="h-1.5 w-1.5 rounded-full bg-accent" />
        El reclamo quedó registrado en el historial con su clasificación.
      </div>
    </section>
  )
}
