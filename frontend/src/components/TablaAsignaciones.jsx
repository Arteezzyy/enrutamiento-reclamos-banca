import { ArrowLeftRight, CheckCircle2, Gauge, TrendingUp } from 'lucide-react'
import { areaMeta, normalizarArea, porcentaje, prioridadMeta } from '../lib/ui.js'

export default function TablaAsignaciones({ asignaciones }) {
  const total = asignaciones.length
  const promedio = total
    ? asignaciones.reduce((suma, a) => suma + (Number(a.probabilidad_confianza) || 0), 0) / total
    : 0
  const reasignados = asignaciones.filter(
    (a) => normalizarArea(a.area_asignada) !== normalizarArea(a.area_predicha),
  ).length

  return (
    <section className="card animate-fade-up overflow-hidden">
      <div className="flex flex-col gap-3 border-b border-line px-6 py-5 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="flex items-center gap-2 text-base font-bold text-navy">
            <CheckCircle2 className="h-4 w-4 text-accent" />
            Asignaciones realizadas
          </h2>
          <p className="mt-0.5 text-sm text-muted">
            Resultado del solver CBC sobre {total} reclamo{total === 1 ? '' : 's'}.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <span className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-[#F8FAFC] px-2.5 py-1.5 text-[11px] font-semibold text-muted">
            <Gauge className="h-3.5 w-3.5 text-accent" />
            Confianza media {porcentaje(promedio)}
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-[#F8FAFC] px-2.5 py-1.5 text-[11px] font-semibold text-muted">
            <ArrowLeftRight className="h-3.5 w-3.5 text-gold" />
            {reasignados} reasignado{reasignados === 1 ? '' : 's'}
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px] border-collapse text-left">
          <thead className="bg-[#F8FAFC]">
            <tr>
              <th className="th">Reclamo</th>
              <th className="th">Área predicha</th>
              <th className="th">Área asignada</th>
              <th className="th">Prioridad</th>
              <th className="th">SLA</th>
              <th className="th">Confianza</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {asignaciones.map((asignacion) => {
              const predicha = areaMeta(asignacion.area_predicha)
              const asignada = areaMeta(asignacion.area_asignada)
              const prioridad = prioridadMeta(asignacion.prioridad)
              const reasignado = predicha.key !== asignada.key
              return (
                <tr key={asignacion.id} className="transition-colors hover:bg-[#F8FAFC]">
                  <td className="px-4 py-3.5">
                    <p className="text-[10px] font-bold uppercase tracking-[0.08em] text-muted/60">
                      {asignacion.id}
                    </p>
                    <p
                      className="mt-0.5 max-w-[300px] truncate text-sm font-medium text-ink"
                      title={asignacion.texto}
                    >
                      {asignacion.texto || '—'}
                    </p>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className="inline-flex items-center gap-1.5 text-sm text-muted">
                      <span className={`h-1.5 w-1.5 rounded-full ${predicha.tono.dot}`} />
                      {predicha.label}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className={`badge normal-case tracking-normal ${asignada.tono.pill}`}>
                        <span className={`h-1.5 w-1.5 rounded-full ${asignada.tono.dot}`} />
                        {asignada.label}
                      </span>
                      {reasignado && (
                        <span className="rounded-md border border-gold/30 bg-gold-soft px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-gold-dark">
                          Reasignado
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className={`badge ${prioridad.pill}`}>
                      <span className={`h-1.5 w-1.5 rounded-full ${prioridad.dot}`} />
                      {prioridad.label}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-4 py-3.5">
                    <span className="text-sm font-semibold tabular-nums text-ink">{asignacion.sla_horas} h</span>
                  </td>
                  <td className="px-4 py-3.5">
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-24 overflow-hidden rounded-full bg-line">
                        <div
                          className="h-full rounded-full bg-accent transition-all duration-700"
                          style={{
                            width: `${Math.max((Number(asignacion.probabilidad_confianza) || 0) * 100, 2)}%`,
                          }}
                        />
                      </div>
                      <span className="w-9 text-right text-xs font-semibold tabular-nums text-muted">
                        {porcentaje(asignacion.probabilidad_confianza)}
                      </span>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div className="flex flex-wrap items-center gap-2 border-t border-line bg-[#FAFBFD] px-6 py-3 text-xs text-muted">
        <TrendingUp className="h-3.5 w-3.5 text-accent" />
        Costo total minimizado respetando capacidad por área y penalización por SLA.
      </div>
    </section>
  )
}
