import { useState, useEffect } from 'react'
import { plus, list, users, truck, alertTriangle, checkCircle2, calendar } from 'lucide-react'
import {
  clasificarReclamo,
  asignarReclamos,
  listarReclamos,
  obtenerInfo,
} from './services/api.js'
import FormularioReclamo from './components/FormularioReclamo.jsx'
import TablaReclamos from './components/TablaReclamos.jsx'

export default function App() {
  const [reclamos, setReclamos] = useState([])
  const [info, setInfo] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('clasificar')
  const [asignaciones, setAsignaciones] = useState([])
  const [mensaje, setMensaje] = useState(null)

  useEffect(() => {
    cargarDatos()
  }, [])

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
        texto: 'No se pudo conectar con el backend. ¿Está corriendo en localhost:8000?',
      })
    }
  }

  const manejarClasificacion = async (texto) => {
    setLoading(true)
    setMensaje(null)
    try {
      const resultado = await clasificarReclamo(texto)
      setReclamos([resultado, ...reclamos])
      setMensaje({ tipo: 'exito', texto: `Reclamo clasificado: ${resultado.area} / ${resultado.prioridad}` })
    } catch (error) {
      setMensaje({ tipo: 'error', texto: error.message })
    } finally {
      setLoading(false)
    }
  }

  const manejarAsignacion = async () => {
    if (reclamos.length === 0) {
      setMensaje({ tipo: 'error', texto: 'No hay reclamos para asignar' })
      return
    }
    setLoading(true)
    try {
      const reclamosParaAsignar = reclamos.map((r) => ({
        id: r.id,
        texto: r.texto,
        area_predicha: r.area,
        prioridad: r.prioridad,
        probabilidad_area: 0.85,
      }))
      const resultado = await asignarReclamos(reclamosParaAsignar)
      setAsignaciones(resultado)
      setMensaje({ tipo: 'exito', texto: `${resultado.length} reclamos asignados óptimamente` })
      setActiveTab('asignar')
    } catch (error) {
      setMensaje({ tipo: 'error', texto: error.message })
    } finally {
      setLoading(false)
    }
  }

  const cerrarMensaje = () => setMensaje(null)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-800 text-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-blue-400 rounded-lg flex items-center justify-center">
              <truck className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-xl font-bold">Enrutamiento de Reclamos Bancarios</h1>
          </div>
          <p className="text-blue-100 text-sm">
            Sistema inteligente de clasificación y enrutamiento por área y prioridad
          </p>
        </div>
      </header>

      {/* Mensajes */}
      {mensaje && (
        <div className="max-w-7xl mx-auto px-4 mb-4">
          <div
            className={`p-4 rounded-lg flex items-start gap-3 ${
              mensaje.tipo === 'exito'
                ? 'bg-green-100 border border-green-400 text-green-800'
                : 'bg-red-100 border border-red-400 text-red-800'
            }`}
          >
            {mensaje.tipo === 'exito' ? (
              <checkCircle2 className="w-5 h-5 mt-0.5 shrink-0" />
            ) : (
              <alertTriangle className="w-5 h-5 mt-0.5 shrink-0" />
            )}
            <span className="text-sm">{mensaje.texto}</span>
            <button
              onClick={cerrarMensaje}
              className="ml-auto text-sm hover:underline"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 mb-6">
        <div className="flex gap-4 border-b border-gray-300 mb-8">
          <button
            onClick={() => setActiveTab('clasificar')}
            className={`px-4 py-2 text-sm font-medium border-b-2 ${
              activeTab === 'clasificar'
                ? 'border-blue-600 text-blue-700'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <plus className="w-4 h-4 mr-2" /> Nuevo Reclamo
          </button>
          <button
            onClick={() => setActiveTab('lista')}
            className={`px-4 py-2 text-sm font-medium border-b-2 ${
              activeTab === 'lista'
                ? 'border-blue-600 text-blue-700'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <list className="w-4 h-4 mr-2" /> Lista de Reclamos
          </button>
          <button
            onClick={() => setActiveTab('asignar')}
            className={`px-4 py-2 text-sm font-medium border-b-2 ${
              activeTab === 'asignar'
                ? 'border-blue-600 text-blue-700'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <users className="w-4 h-4 mr-2" /> Asignación Óptima
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 pb-12">
        {activeTab === 'clasificar' && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <plus className="w-5 h-5 text-blue-600" />
              Clasificar Nuevo Reclamo
            </h2>
            <FormularioReclamo onSubmit={manejarClasificacion} loading={loading} />
          </div>
        )}

        {activeTab === 'lista' && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                <list className="w-5 h-5 text-blue-600" />
                Historial de Reclamos
              </h2>
            </div>
            <TablaReclamos reclamos={reclamos} />
          </div>
        )}

        {activeTab === 'asignar' && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                  <users className="w-5 h-5 text-blue-600" />
                  Asignación Óptima por Área
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Asigna reclamos a áreas considerando capacidad, SLA y confianza del modelo.
                </p>
              </div>
              <button
                onClick={manejarAsignacion}
                disabled={reclamos.length === 0 || loading}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                {loading ? 'Procesando...' : 'Ejecutar Optimización'}
              </button>
            </div>

            {reclamos.length === 0 && (
              <div className="text-center py-10 text-gray-500">
                <p>No hay reclamos registrados. Agrega algunos primero.</p>
              </div>
            )}

            {asignaciones.length > 0 && (
              <div className="mt-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">
                  Asignaciones Realizadas ({asignaciones.length})
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-gray-200 bg-gray-50">
                        <th className="px-4 py-2 text-sm font-semibold text-gray-600">ID</th>
                        <th className="px-4 py-2 text-sm font-semibold text-gray-600">Área Predicha</th>
                        <th className="px-4 py-2 text-sm font-semibold text-gray-600">Área Asignada</th>
                        <th className="px-4 py-2 text-sm font-semibold text-gray-600">Prioridad</th>
                        <th className="px-4 py-2 text-sm font-semibold text-gray-600">SLA (h)</th>
                        <th className="px-4 py-2 text-sm font-semibold text-gray-600">Confianza</th>
                      </tr>
                    </thead>
                    <tbody>
                      {asignaciones.map((a) => (
                        <tr key={a.id} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="px-4 py-2 text-sm text-gray-800 font-mono">{a.id}</td>
                          <td className="px-4 py-2 text-sm text-gray-700">{a.area_predicha}</td>
                          <td className="px-4 py-2 text-sm font-medium text-blue-700">
                            {a.area_asignada}
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-700">
                            <span
                              className={`px-2 py-1 rounded-full text-xs font-semibold ${
                                a.prioridad === 'Alta'
                                  ? 'bg-red-100 text-red-700'
                                  : a.prioridad === 'Media'
                                  ? 'bg-yellow-100 text-yellow-700'
                                  : 'bg-green-100 text-green-700'
                              }`}
                            >
                              {a.prioridad}
                            </span>
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-700">{a.sla_horas}</td>
                          <td className="px-4 py-2 text-sm text-gray-700">
                            {(a.probabilidad_confianza * 100).toFixed(0)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white py-4 mt-auto">
        <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-gray-500">
          <div className="flex items-center gap-2">
            <users className="w-4 h-4" />
            <span>Ingeniería de Sistemas - UMSS</span>
          </div>
          <div className="flex items-center gap-2">
            <calendar className="w-4 h-4" />
            <span>1° Avance - Clasificación por Optimización</span>
          </div>
        </div>
      </footer>
    </div>
  )
}