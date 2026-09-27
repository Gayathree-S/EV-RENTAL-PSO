import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] text-center max-w-3xl mx-auto px-4">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 mb-6">
        <span>⚡</span>
        <span>Grid-Optimized EV Fleet & Demand Forecasting</span>
      </div>

      <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-gray-900 leading-tight">
        AI-Powered Smart <span className="text-emerald-600">EV Rental</span> Management System
      </h1>

      <p className="mt-4 text-lg text-gray-600 max-w-2xl">
        An intelligent electric vehicle rental and optimization platform featuring
        machine learning demand forecasting and metaheuristic power-grid fleet allocation.
      </p>

      <div className="mt-8 flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
        <Link
          href="/login"
          className="w-full sm:w-auto px-8 py-3 rounded-xl bg-emerald-600 text-white font-semibold hover:bg-emerald-700 transition-all shadow-md hover:shadow-lg text-center"
        >
          Login to Account
        </Link>
        <Link
          href="/register"
          className="w-full sm:w-auto px-8 py-3 rounded-xl bg-white text-gray-800 font-semibold border border-gray-300 hover:bg-gray-50 transition-all shadow-sm text-center"
        >
          Create an Account
        </Link>
      </div>

      <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-6 w-full text-left">
        <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm">
          <div className="text-2xl mb-2">🔋</div>
          <h2 className="font-bold text-gray-900 text-base">Demand Prediction</h2>
          <p className="text-xs text-gray-500 mt-1">
            Machine learning models accurately forecast trip charging energy requirements.
          </p>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm">
          <div className="text-2xl mb-2">⚡</div>
          <h2 className="font-bold text-gray-900 text-base">Grid Optimization</h2>
          <p className="text-xs text-gray-500 mt-1">
            PSO algorithms place rental hubs minimizing distribution grid active power losses.
          </p>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm">
          <div className="text-2xl mb-2">🚗</div>
          <h2 className="font-bold text-gray-900 text-base">Real-Time Fleet</h2>
          <p className="text-xs text-gray-500 mt-1">
            Seamlessly browse available EVs across 10 network-optimized rental centers.
          </p>
        </div>
      </div>
    </div>
  );
}
