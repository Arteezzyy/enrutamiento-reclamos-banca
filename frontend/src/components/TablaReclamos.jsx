export default function TablaReclamos({ reclamos }) {
  if (!reclamos || reclamos.length === 0) {
    return (
      <div className="text-center py-10 text-gray-500">
        <p>No hay reclamos registrados aún.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50 sticky top-0">
            <th className="px-4 py-3 text-sm font-semibold text-gray-600">ID</th>
            <th className="px-4 py-3 text-sm font-semibold text-gray-600">Texto del Reclamo</th>
            <th className="px-4 py-3 text-sm font-semibold text-gray-600">Área</th>
            <th className="px-4 py-3 text-sm font-semibold text-gray-600">Prioridad</th>
            <th className="px-4 py-3 text-sm font-semibold text-gray-600">Fecha</th>
          </tr>
        </thead>
        <tbody>
          {reclamos.slice(0, 50).map((r) => (
            <tr key={r.id} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="px-4 py-3 text-sm text-gray-800 font-mono">{r.id}</td>
              <td className="px-4 py-3 text-sm text-gray-700 max-w-[400px] truncate">
                {r.texto}
              </td>
              <td className="px-4 py-3 text-sm text-gray-700">{r.area}</td>
              <td className="px-4 py-3 text-sm text-gray-700">
                <span
                  className={`px-2 py-1 rounded-full text-xs font-semibold ${
                    r.prioridad === 'Alta'
                      ? 'bg-red-100 text-red-700 border border-red-200'
                      : r.prioridad === 'Media'
                      ? 'bg-yellow-100 text-yellow-700 border border-yellow-200'
                      : 'bg-green-100 text-green-700 border border-green-200'
                  }`}
                >
                  {r.prioridad}
                </span>
              </td>
              <td className="px-4 py-3 text-sm text-gray-500">
                {r.fecha ? new Date(r.fecha).toLocaleString('es-BO') : '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {reclamos.length > 50 && (
        <p className="mt-3 text-sm text-gray-500">
          Mostrando los primeros 50 de {reclamos.length} reclamos.
        </p>
      )}
    </div>
  )
}