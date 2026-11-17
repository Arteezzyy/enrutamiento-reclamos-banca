import { useMemo, useState } from 'react'
import { AlertTriangle, ArrowRight, CheckCircle2, Clock, Inbox, Layers, Search, X } from 'lucide-react'
import { TONO_AREA, TONO_PRIORIDAD, areaMeta, formatFecha, prioridadMeta } from '../lib/ui.js'

function Kpi({ icon: Icon, etiqueta, valor, detalle, tono }) {
  return (
    <div className="card flex items-center gap-4 p-5">
      <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${tono.soft} ${tono.text}`}>
        <Icon className="h-5 w-5" strokeWidth={2.2} />
      </div>
      <div className="min-w-0">
        <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-muted/80">{etiqueta}</p>
        <p className="mt-0.5 text-2xl font-bold leading-none tabular-nums text-navy">{valor}</p>
        <p className="mt-1 truncate text-xs text-muted">{detalle}</p>
      </div>
    </div>
  )
}

export default function VistaLista({ reclamos, onClasificar }) {
  const [busqueda, setBusqueda] = useState('')

  const stats = useMemo(() => {
    const porPrioridad = { Alta: 0, Media: 0, Baja: 0 }
    for (const reclamo of reclamos) {
      porPrioridad[prioridadMeta(reclamo.prioridad).key] += 1
    }
    return { total: reclamos.length, ...porPrioridad }
  }, [reclamos])

  const filtrados = useMemo(() => {
    const consulta = busqueda.trim().toLowerCase()
    const ordenados = [...reclamos].sort(
      (a, b) => new Date(b.fecha || 0).getTime() - new Date(a.fecha || 0).getTime(),
    )
    if (!consulta) return ordenados
    return ordenados.filter((reclamo) =>
      [reclamo.id, reclamo.texto, reclamo.area, reclamo.prioridad]
        .some((valor) => String(valor ?? '').toLowerCase().includes(consulta)),
    )
  }, [reclamos, busqueda])

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Kpi
          icon={Layers}
          etiqueta="Total reclamos"
          valor={stats.total}
          detalle="Registrados en esta sesión"
          tono={TONO_AREA.azul}
        />
        <Kpi
          icon={AlertTriangle}
          etiqueta="Prioridad alta"
          valor={stats.Alta}
          detalle="SLA de atención: 2 horas"
          tono={TONO_PRIORIDAD.Alta}
        />
        <Kpi
          icon={Clock}
          etiqueta="Prioridad media"
          valor={stats.Media}
          detalle="SLA de atención: 8 horas"
          tono={TONO_PRIORIDAD.Media}
        />
        <Kpi
          icon={CheckCircle2}
          etiqueta="Prioridad baja"
          valor={stats.Baja}
          detalle="SLA de atención: 24 horas"
          tono={TONO_PRIORIDAD.Baja}
        />
      </div>

      <section className="card overflow-hidden">
        <div className="flex flex-col gap-4 border-b border-line px-6 py-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-base font-bold text-navy">Historial de reclamos</h2>
            <p className="mt-0.5 text-sm text-muted">Consulta el área y la prioridad asignada por el modelo.</p>
          </div>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted/70" />
              <input
                type="search"
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                placeholder="Buscar reclamo..."
                className="input w-full py-2.5 pl-10 pr-9 text-sm sm:w-72"
              />
              {busqueda && (
                <button
                  type="button"
                  onClick={() => setBusqueda('')}
                  aria-label="Limpiar búsqueda"
                  className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-1 text-muted/70 transition-colors hover:bg-line/60 hover:text-ink"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              )}
            </div>
            <button type="button" onClick={onClasificar} className="btn-ghost whitespace-nowrap">
              Nuevo reclamo
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>

        {reclamos.length === 0 ? (
          <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#F8FAFC] text-muted/60">
              <Inbox className="h-7 w-7" />
            </div>
            <p className="mt-4 text-sm font-semibold text-navy">Aún no hay reclamos registrados</p>
            <p className="mt-1 max-w-sm text-sm text-muted">
              Clasifica el primer reclamo para verlo aquí con su área y prioridad asignadas.
            </p>
            <button type="button" onClick={onClasificar} className="btn-primary mt-5">
              Clasificar el primer reclamo
            </button>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[780px] border-collapse text-left">
                <thead className="bg-[#F8FAFC]">
                  <tr>
                    <th className="th">Reclamo</th>
                    <th className="th">Área asignada</th>
                    <th className="th">Prioridad</th>
                    <th className="th">Registrado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {filtrados.map((reclamo) => {
                    const area = areaMeta(reclamo.area)
                    const prioridad = prioridadMeta(reclamo.prioridad)
                    return (
                      <tr key={reclamo.id} className="transition-colors hover:bg-[#F8FAFC]">
                        <td className="px-4 py-3.5">
                          <p className="text-[10px] font-bold uppercase tracking-[0.08em] text-muted/60">
                            {reclamo.id}
                          </p>
                          <p
                            className="mt-0.5 max-w-[430px] truncate text-sm font-medium text-ink"
                            title={reclamo.texto}
                          >
                            {reclamo.texto}
                          </p>
                        </td>
                        <td className="px-4 py-3.5">
                          <span className={`badge normal-case tracking-normal ${area.tono.pill}`}>
                            <span className={`h-1.5 w-1.5 rounded-full ${area.tono.dot}`} />
                            {area.label}
                          </span>
                        </td>
                        <td className="px-4 py-3.5">
                          <span className={`badge ${prioridad.pill}`}>
                            <span className={`h-1.5 w-1.5 rounded-full ${prioridad.dot}`} />
                            {prioridad.label}
                          </span>
                        </td>
                        <td className="whitespace-nowrap px-4 py-3.5 text-sm text-muted">
                          {formatFecha(reclamo.fecha)}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            {filtrados.length === 0 ? (
              <div className="flex flex-col items-center gap-2 px-6 py-12 text-center">
                <Search className="h-6 w-6 text-muted/50" />
                <p className="text-sm font-semibold text-navy">Sin coincidencias</p>
                <p className="text-sm text-muted">Prueba con otro texto, área o prioridad.</p>
              </div>
            ) : (
              <div className="flex flex-wrap items-center justify-between gap-2 border-t border-line bg-[#FAFBFD] px-6 py-3 text-xs text-muted">
                <span>
                  Mostrando <span className="font-semibold text-ink">{filtrados.length}</span> de{' '}
                  <span className="font-semibold text-ink">{reclamos.length}</span> reclamos
                </span>
                <span>Ordenados del más reciente al más antiguo</span>
              </div>
            )}
          </>
        )}
      </section>
    </div>
  )
}
