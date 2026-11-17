import { Building2, Clock, Layers, Loader2, Zap } from 'lucide-react'
import TablaAsignaciones from './TablaAsignaciones.jsx'
import { CAPACIDADES_DEFAULT, SLA_POR_PRIORIDAD, areaMeta } from '../lib/ui.js'

export default function VistaAsignar({ reclamos, asignaciones, onAsignar, loading, info }) {
  const capacidades = info?.capacidades ?? CAPACIDADES_DEFAULT
  const capacidadTotal = Object.values(capacidades).reduce((suma, valor) => suma + valor, 0)

  return (
    <div className="space-y-6">
      <section className="card relative overflow-hidden border-0 bg-navy p-6 text-white sm:p-8">
        <div className="pointer-events-none absolute -right-20 -top-24 h-72 w-72 rounded-full bg-accent/25 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-28 right-24 h-56 w-56 rounded-full bg-gold/10 blur-3xl" />

        <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-gold">
              <span className="h-1 w-1 rounded-full bg-gold" />
              Programación lineal entera · PuLP
            </p>
            <h2 className="mt-1.5 max-w-xl font-sans text-xl font-semibold leading-snug sm:text-2xl">
              Minimiza el costo, respeta el SLA y la capacidad de cada área
            </h2>
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-white/60">
              El solver asigna cada reclamo a un área operativa combinando la predicción del modelo, la
              confianza y la prioridad de atención.
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              <span className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/[0.06] px-2.5 py-1 text-[11px] font-semibold text-white/75">
                <Layers className="h-3.5 w-3.5 text-accent" />
                {reclamos.length} en cola
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/[0.06] px-2.5 py-1 text-[11px] font-semibold text-white/75">
                <Building2 className="h-3.5 w-3.5 text-gold" />
                Capacidad total {capacidadTotal}/turno
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/[0.06] px-2.5 py-1 text-[11px] font-semibold text-white/75">
                <Clock className="h-3.5 w-3.5 text-white/60" />
                SLA crítico {SLA_POR_PRIORIDAD.Alta} h
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={onAsignar}
            disabled={reclamos.length === 0 || loading}
            className="btn-primary shrink-0 self-start lg:self-center"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Optimizando...
              </>
            ) : (
              <>
                <Zap className="h-4 w-4" />
                Ejecutar optimización
              </>
            )}
          </button>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-3">
        {Object.entries(capacidades).map(([area, capacidad]) => {
          const meta = areaMeta(area)
          return (
            <div key={area} className="card flex items-center gap-4 p-5">
              <div
                className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${meta.tono.soft} ${meta.tono.text}`}
              >
                <Building2 className="h-5 w-5" strokeWidth={2.1} />
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-ink" title={meta.label}>
                  {meta.label}
                </p>
                <p className="mt-0.5 text-xs text-muted">
                  Capacidad <span className="font-bold text-navy">{capacidad}</span> reclamos / turno
                </p>
              </div>
            </div>
          )
        })}
      </div>

      {asignaciones.length > 0 ? (
        <TablaAsignaciones asignaciones={asignaciones} />
      ) : (
        <section className="card flex flex-col items-center justify-center px-6 py-16 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#F8FAFC] text-muted/60">
            <Layers className="h-7 w-7" />
          </div>
          <p className="mt-4 text-sm font-semibold text-navy">
            {reclamos.length === 0 ? 'Todavía no hay reclamos en cola' : 'Listo para optimizar'}
          </p>
          <p className="mt-1 max-w-md text-sm leading-relaxed text-muted">
            {reclamos.length === 0
              ? 'Clasifica reclamos primero; luego podrás distribuirlos entre las áreas respetando capacidad y SLA.'
              : `Hay ${reclamos.length} reclamo${reclamos.length === 1 ? '' : 's'} listo${
                  reclamos.length === 1 ? '' : 's'
                } para asignar. Ejecuta la optimización para ver el enrutamiento propuesto.`}
          </p>
        </section>
      )}
    </div>
  )
}
