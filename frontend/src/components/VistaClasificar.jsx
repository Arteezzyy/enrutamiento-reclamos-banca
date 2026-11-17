import { BrainCircuit, Cpu, FileText, Layers, Sparkles } from 'lucide-react'
import FormularioReclamo from './FormularioReclamo.jsx'
import ResultadoClasificacion from './ResultadoClasificacion.jsx'
import { CAPACIDADES_DEFAULT, areaMeta } from '../lib/ui.js'

const PASOS = [
  {
    icon: FileText,
    titulo: 'Texto del reclamo',
    detalle: 'Se recibe el mensaje tal como lo escribe el cliente.',
  },
  {
    icon: Cpu,
    titulo: 'Vectorización TF-IDF',
    detalle: 'Hasta 5.000 términos con unigramas y bigramas.',
  },
  {
    icon: BrainCircuit,
    titulo: 'Modelo supervisado',
    detalle: 'Regresión logística para área y prioridad.',
  },
  {
    icon: Layers,
    titulo: 'Enrutamiento',
    detalle: 'Asignación óptima con SLA y capacidad por área.',
  },
]

export default function VistaClasificar({
  onSubmit,
  loading,
  ultimoResultado,
  onVerHistorial,
  info,
}) {
  const capacidades = info?.capacidades ?? CAPACIDADES_DEFAULT
  const areas = Object.keys(capacidades)

  return (
    <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
      <div className="space-y-6">
        <section className="card overflow-hidden">
          <div className="border-b border-line bg-gradient-to-r from-[#F8FAFC] via-white to-white px-6 py-5 sm:px-8">
            <div className="flex items-start gap-4">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-navy text-white shadow-lg shadow-navy/20">
                <Sparkles className="h-5 w-5 text-gold" strokeWidth={2.2} />
              </div>
              <div>
                <h2 className="text-base font-bold text-navy sm:text-lg">Clasificar nuevo reclamo</h2>
                <p className="mt-0.5 max-w-xl text-sm leading-relaxed text-muted">
                  Escribe el reclamo tal como lo recibes; el modelo detectará el área de destino y la prioridad
                  de atención.
                </p>
              </div>
            </div>
          </div>
          <div className="p-6 sm:p-8">
            <FormularioReclamo onSubmit={onSubmit} loading={loading} />
          </div>
        </section>

        <ResultadoClasificacion resultado={ultimoResultado} onVerHistorial={onVerHistorial} />
      </div>

      <aside className="space-y-6">
        <section className="card p-6">
          <h2 className="text-sm font-bold text-navy">Cómo funciona</h2>
          <p className="mt-1 text-xs leading-relaxed text-muted">
            Pipeline de clasificación y enrutamiento en cuatro etapas.
          </p>
          <ol className="mt-5 space-y-4">
            {PASOS.map(({ icon: Icon, titulo, detalle }, indice) => (
              <li key={titulo} className="relative flex gap-3.5">
                <div className="relative flex flex-col items-center">
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-line bg-[#F8FAFC] text-navy">
                    <Icon className="h-4 w-4" strokeWidth={2.2} />
                  </span>
                  {indice < PASOS.length - 1 && (
                    <span className="mt-1 w-px flex-1 bg-line" aria-hidden="true" />
                  )}
                </div>
                <div className="pb-1">
                  <p className="flex items-baseline gap-1.5 text-sm font-semibold text-ink">
                    <span className="text-[10px] font-bold tabular-nums text-gold">0{indice + 1}</span>
                    {titulo}
                  </p>
                  <p className="mt-0.5 text-xs leading-relaxed text-muted">{detalle}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <section className="card overflow-hidden">
          <div className="bg-navy px-6 py-5 text-white">
            <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-white/50">Áreas de destino</p>
            <p className="mt-1 text-sm font-semibold">{areas.length} colas operativas activas</p>
          </div>
          <ul className="divide-y divide-line">
            {areas.map((area) => {
              const meta = areaMeta(area)
              return (
                <li key={area} className="flex items-center gap-3 px-6 py-3.5">
                  <span className={`h-2 w-2 shrink-0 rounded-full ${meta.tono.dot}`} />
                  <span className="flex-1 text-sm font-medium text-ink">{meta.label}</span>
                  <span className="whitespace-nowrap rounded-md bg-[#F8FAFC] px-1.5 py-0.5 text-[11px] font-semibold tabular-nums text-muted">
                    {capacidades[area]}/turno
                  </span>
                </li>
              )
            })}
          </ul>
        </section>
      </aside>
    </div>
  )
}
