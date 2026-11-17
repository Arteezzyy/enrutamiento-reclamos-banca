import { useEffect, useMemo, useState } from 'react'
import { AlertTriangle, CheckCircle2, RefreshCw, X } from 'lucide-react'
import {
  clasificarReclamo,
  asignarReclamos,
  listarReclamos,
  obtenerInfo,
} from './services/api.js'
import Sidebar from './components/Sidebar.jsx'
import VistaClasificar from './components/VistaClasificar.jsx'
import VistaLista from './components/VistaLista.jsx'
import VistaAsignar from './components/VistaAsignar.jsx'
import { areaMeta, prioridadMeta } from './lib/ui.js'

const SECCIONES = {
  clasificar: {
    eyebrow: 'Recepción',
    title: 'Nuevo reclamo',
    desc: 'Clasifica el reclamo por área y prioridad con el modelo de IA.',
  },
  lista: {
    eyebrow: 'Seguimiento',
    title: 'Historial de reclamos',
    desc: 'Consulta los reclamos clasificados y su estado operativo.',
  },
  asignar: {
    eyebrow: 'Optimización',
    title: 'Asignación óptima',
    desc: 'Distribuye los reclamos entre áreas con PuLP.',
  },
}

export default function App() {
  const [reclamos, setReclamos] = useState([])
  const [info, setInfo] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window === 'undefined') return 'clasificar'
    const hash = window.location.hash.replace('#', '')
    return Object.prototype.hasOwnProperty.call(SECCIONES, hash) ? hash : 'clasificar'
  })
  const [asignaciones, setAsignaciones] = useState([])
  const [ultimoResultado, setUltimoResultado] = useState(null)
  const [mensaje, setMensaje] = useState(null)

  const seccion = SECCIONES[activeTab]

  const cargarDatos = async () => {
    try {
      const [infoData, reclamosData] = await Promise.all([
        obtenerInfo(),
        listarReclamos(),
      ])
      setInfo(infoData)
      setReclamos(reclamosData)
    } catch (error) {
      console.error('Error cargando datos:', error)
      setMensaje({
        tipo: 'error',
        texto: 'No se pudo conectar con el backend. Verifica que esté corriendo en localhost:8000.',
      })
    }
  }

  useEffect(() => {
    cargarDatos()
  }, [])

  useEffect(() => {
    if (!mensaje) return undefined
    const temporizador = setTimeout(() => setMensaje(null), 7000)
    return () => clearTimeout(temporizador)
  }, [mensaje])

  const manejarClasificacion = async (texto) => {
    setLoading(true)
    setMensaje(null)
    try {
      const resultado = await clasificarReclamo(texto)
      setReclamos((previos) => [
        { ...resultado, fecha: resultado.fecha ?? new Date().toISOString() },
        ...previos,
      ])
      setUltimoResultado(resultado)
      setAsignaciones([])
      setMensaje({
        tipo: 'exito',
        texto: `Reclamo clasificado en ${areaMeta(resultado.area).label} con prioridad ${
          prioridadMeta(resultado.prioridad).label
        }.`,
      })
    } catch (error) {
      setMensaje({ tipo: 'error', texto: error.message })
    } finally {
      setLoading(false)
    }
  }

  const manejarAsignacion = async () => {
    if (reclamos.length === 0) {
      setMensaje({ tipo: 'error', texto: 'No hay reclamos para asignar.' })
      return
    }
    setLoading(true)
    setMensaje(null)
    try {
      const reclamosParaAsignar = reclamos.map((reclamo) => ({
        id: reclamo.id,
        texto: reclamo.texto,
        area_predicha: reclamo.area,
        prioridad: reclamo.prioridad,
        probabilidad_area: reclamo.probabilidades_area?.[reclamo.area] ?? 0.85,
      }))
      const resultado = await asignarReclamos(reclamosParaAsignar)
      setAsignaciones(resultado)
      setMensaje({
        tipo: 'exito',
        texto: `${resultado.length} reclamo${resultado.length === 1 ? '' : 's'} asignado${
          resultado.length === 1 ? '' : 's'
        } de forma óptima.`,
      })
      setActiveTab('asignar')
    } catch (error) {
      setMensaje({ tipo: 'error', texto: error.message })
    } finally {
      setLoading(false)
    }
  }

  const cambiarTab = (tab) => {
    setActiveTab(tab)
    if (typeof window !== 'undefined') {
      window.history.replaceState(null, '', `#${tab}`)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  const cerrarMensaje = () => setMensaje(null)

  const anioActual = useMemo(() => new Date().getFullYear(), [])
  const esExito = mensaje?.tipo === 'exito'

  return (
    <div className="min-h-screen lg:flex">
      <Sidebar activeTab={activeTab} onChange={cambiarTab} reclamos={reclamos} />

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-10 border-b border-line/80 bg-app/85 backdrop-blur-xl">
          <div className="mx-auto flex w-full max-w-[1440px] flex-wrap items-center gap-3 px-4 py-4 sm:px-6 lg:px-8">
            <div className="mr-auto min-w-0">
              <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-[0.2em] text-accent">
                <span className="h-1 w-1 rounded-full bg-gold" />
                {seccion.eyebrow}
              </p>
              <h1 className="mt-0.5 truncate font-sans text-xl font-semibold tracking-tight text-navy sm:text-2xl">
                {seccion.title}
              </h1>
              <p className="mt-0.5 hidden truncate text-xs text-muted sm:block">{seccion.desc}</p>
            </div>

            <div className="flex items-center gap-2">
              <span
                className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-[11px] font-semibold ${
                  info
                    ? 'border-[#1E8E5A]/20 bg-[#E3F6EC] text-[#1E8E5A]'
                    : 'border-[#D64545]/20 bg-[#FDE8E8] text-[#D64545]'
                }`}
              >
                <span className={`h-1.5 w-1.5 rounded-full ${info ? 'bg-[#1E8E5A]' : 'bg-[#D64545]'}`} />
                {info ? 'API conectada' : 'Sin conexión'}
              </span>
              <button
                type="button"
                onClick={cargarDatos}
                title="Actualizar datos"
                className="btn-ghost px-3 py-2"
              >
                <RefreshCw className="h-4 w-4 text-muted" />
                <span className="hidden sm:inline">Actualizar</span>
              </button>
            </div>
          </div>
        </header>

        <main className="mx-auto w-full max-w-[1440px] flex-1 px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
          {activeTab === 'clasificar' && (
            <VistaClasificar
              onSubmit={manejarClasificacion}
              loading={loading}
              ultimoResultado={ultimoResultado}
              onVerHistorial={() => cambiarTab('lista')}
              info={info}
            />
          )}

          {activeTab === 'lista' && (
            <VistaLista reclamos={reclamos} onClasificar={() => cambiarTab('clasificar')} />
          )}

          {activeTab === 'asignar' && (
            <VistaAsignar
              reclamos={reclamos}
              asignaciones={asignaciones}
              onAsignar={manejarAsignacion}
              loading={loading}
              info={info}
            />
          )}
        </main>

        <footer className="mt-auto border-t border-line bg-white/70">
          <div className="mx-auto flex w-full max-w-[1440px] flex-col items-center justify-between gap-2 px-4 py-4 text-xs text-muted sm:flex-row sm:px-6 lg:px-8">
            <p>Ingeniería de Sistemas · Universidad Mayor de San Simón</p>
            <p className="flex flex-wrap items-center justify-center gap-2">
              <span>Sistema</span>
              <span className="h-1 w-1 rounded-full bg-line" />
              <span>TF-IDF + Regresión Logística · PuLP</span>
              <span className="h-1 w-1 rounded-full bg-line" />
              <span>{anioActual}</span>
            </p>
          </div>
        </footer>
      </div>

      {mensaje && (
        <div className="fixed bottom-5 right-5 z-50 w-[calc(100%-2.5rem)] max-w-sm animate-slide-up">
          <div className="flex items-start gap-3 rounded-2xl border border-line bg-white p-4 shadow-lift">
            <div
              className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${
                esExito ? 'bg-[#E3F6EC] text-[#1E8E5A]' : 'bg-[#FDE8E8] text-[#D64545]'
              }`}
            >
              {esExito ? (
                <CheckCircle2 className="h-5 w-5" />
              ) : (
                <AlertTriangle className="h-5 w-5" />
              )}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-bold text-navy">{esExito ? 'Operación completada' : 'Ocurrió un problema'}</p>
              <p className="mt-0.5 text-sm leading-snug text-muted">{mensaje.texto}</p>
            </div>
            <button
              type="button"
              onClick={cerrarMensaje}
              aria-label="Cerrar mensaje"
              className="rounded-md p-1 text-muted/70 transition-colors hover:bg-line/60 hover:text-ink"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
