"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { api } from "../lib/api";
import { getStoredUser } from "../lib/auth";

export default function AdminDashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [bookings, setBookings] = useState([]);
  const [optimizerResults, setOptimizerResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const storedUser = getStoredUser();
    // Protect route: must be logged in and is_admin === true
    if (!storedUser || !storedUser.is_admin) {
      router.push("/login");
      return;
    }
    setUser(storedUser);

    const loadAdminData = async () => {
      try {
        setLoading(true);
        const [bookingsData, optimizerData] = await Promise.all([
          api.get("/bookings"),
          api.get("/optimizer/results"),
        ]);

        // Sort newest first client-side for safety
        const sortedBookings = [...bookingsData].sort(
          (a, b) => new Date(b.created_at) - new Date(a.created_at)
        );
        setBookings(sortedBookings);
        setOptimizerResults(optimizerData);
      } catch (err) {
        setError(err.message || "Failed to load admin dashboard data.");
      } finally {
        setLoading(false);
      }
    };

    loadAdminData();
  }, [router]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <div className="w-10 h-10 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
        <p className="mt-4 text-sm text-gray-500">Loading admin dashboard & analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto my-12 p-6 bg-red-50 border border-red-200 rounded-2xl text-center">
        <h2 className="text-lg font-bold text-red-800">Error Loading Dashboard</h2>
        <p className="text-sm text-red-600 mt-2">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  // Helper to build Recharts data for convergence history
  const buildChartData = (caseData) => {
    if (!caseData || !caseData.pso || !caseData.ga) return [];
    const psoHist = caseData.pso.convergence_history || [];
    const gaHist = caseData.ga.convergence_history || [];
    const maxLen = Math.max(psoHist.length, gaHist.length);
    const data = [];
    for (let i = 0; i < maxLen; i++) {
      data.push({
        iteration: i + 1,
        PSO: psoHist[i] !== undefined ? parseFloat(psoHist[i].toFixed(2)) : null,
        GA: gaHist[i] !== undefined ? parseFloat(gaHist[i].toFixed(2)) : null,
      });
    }
    return data;
  };

  // Helper to generate dynamic plain-language interpretation
  const generateInterpretation = (pso, ga, caseLabel) => {
    const psoFit = pso.best_fitness;
    const gaFit = ga.best_fitness;
    const psoTime = pso.time_seconds;
    const gaTime = ga.time_seconds;
    const psoViol = pso.num_violations;
    const gaViol = ga.num_violations;

    let fitnessComp = "";
    if (Math.abs(psoFit - gaFit) < 0.001) {
      const faster = psoTime < gaTime ? "PSO" : "GA";
      const fasterTime = Math.min(psoTime, gaTime);
      const slowerTime = Math.max(psoTime, gaTime);
      fitnessComp = `Both algorithms reached the identical optimal fitness of ${psoFit.toFixed(2)} with 0 voltage violations. ${faster} converged slightly faster (${fasterTime.toFixed(1)}s vs ${slowerTime.toFixed(1)}s).`;
    } else if (psoFit < gaFit) {
      const diff = gaFit - psoFit;
      fitnessComp = `PSO found a superior solution with lower fitness (${psoFit.toFixed(2)} vs GA's ${gaFit.toFixed(2)}, an improvement of ${diff.toFixed(2)}). PSO recorded ${psoViol} voltage violations vs ${gaViol} for GA in similar execution time (${psoTime.toFixed(1)}s vs ${gaTime.toFixed(1)}s).`;
    } else {
      const diff = psoFit - gaFit;
      fitnessComp = `GA found a superior solution with lower fitness (${gaFit.toFixed(2)} vs PSO's ${psoFit.toFixed(2)}, an improvement of ${diff.toFixed(2)}).`;
    }

    return `Lower fitness is better. ${fitnessComp}`;
  };

  return (
    <div className="space-y-10">
      {/* Header Banner */}
      <div className="bg-white p-6 sm:p-8 rounded-2xl border border-gray-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 mb-2">
            <span>🛡️</span>
            <span>Administrator Control Center</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
            System Overview & Metaheuristic Analytics
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Monitor real-time EV rental reservations and review PSO vs GA distribution grid placement benchmarks
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-4 py-2.5 bg-purple-50 border border-purple-200 rounded-xl text-center">
            <span className="text-xs font-semibold text-purple-800 uppercase tracking-wider block">
              Total Bookings
            </span>
            <span className="text-xl font-bold text-purple-700">{bookings.length}</span>
          </div>
        </div>
      </div>

      {/* SECTION 1: All Bookings Table */}
      <section className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-gray-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-xl font-bold text-gray-900">All Fleet Reservations</h2>
            <p className="text-xs text-gray-500 mt-0.5">
              Live log of user bookings with ML-predicted charging demand (sorted newest first)
            </p>
          </div>
          <span className="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-semibold rounded-full">
            {bookings.length} Record{bookings.length === 1 ? "" : "s"}
          </span>
        </div>

        {bookings.length === 0 ? (
          <div className="p-12 text-center text-gray-500 text-sm">
            No bookings recorded in the system yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 border-b border-gray-200 text-xs uppercase tracking-wider text-gray-500">
                <tr>
                  <th className="py-3.5 px-4 font-semibold">ID</th>
                  <th className="py-3.5 px-4 font-semibold">Renter Name & Email</th>
                  <th className="py-3.5 px-4 font-semibold">Vehicle</th>
                  <th className="py-3.5 px-4 font-semibold">Pickup Hr</th>
                  <th className="py-3.5 px-4 font-semibold">Return Hr</th>
                  <th className="py-3.5 px-4 font-semibold">ML Predicted Demand</th>
                  <th className="py-3.5 px-4 font-semibold">Created At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {bookings.map((b) => (
                  <tr key={b.id} className="hover:bg-gray-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-mono text-xs font-semibold text-gray-500">
                      #{b.id}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-gray-900">
                        {b.user?.name || "Unknown User"}
                      </div>
                      <div className="text-xs text-gray-500">{b.user?.email || "—"}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="inline-block px-2.5 py-1 rounded-md bg-emerald-50 border border-emerald-200 text-xs font-mono font-bold text-emerald-800">
                        {b.vehicle?.vehicle_code || `EV #${b.vehicle_id}`}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-gray-700">{b.dropoff_time_hr}:00</td>
                    <td className="py-3.5 px-4 text-gray-700">{b.pickup_time_hr}:00</td>
                    <td className="py-3.5 px-4">
                      {b.predicted_charging_energy_kwh != null ? (
                        <span className="inline-flex items-center gap-1 font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded text-xs">
                          <span>⚡</span> {b.predicted_charging_energy_kwh.toFixed(2)} kWh
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs">N/A</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-gray-500">
                      {b.created_at ? new Date(b.created_at).toLocaleString() : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* SECTION 2: PSO vs GA Comparison */}
      <section className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 tracking-tight">
            Optimizer Benchmark Analytics: PSO vs GA
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Empirical convergence curves and performance metrics comparing Particle Swarm Optimization against Genetic Algorithm on IEEE 33-Bus Radial Grid
          </p>
        </div>

        {optimizerResults ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Case N=2 Locations */}
            {optimizerResults.case_N2 && (
              <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between border-b border-gray-100 pb-3 mb-4">
                    <h3 className="text-lg font-bold text-gray-900">
                      Comparison: N=2 Center Locations
                    </h3>
                    <span className="text-xs px-2.5 py-1 bg-emerald-100 text-emerald-800 font-semibold rounded-full">
                      Small Fleet Benchmark
                    </span>
                  </div>

                  {/* Summary Comparison Table */}
                  <div className="overflow-x-auto mb-6">
                    <table className="w-full text-xs text-left border border-gray-200 rounded-lg overflow-hidden">
                      <thead className="bg-gray-50 text-gray-600 uppercase font-semibold">
                        <tr>
                          <th className="py-2 px-3">Metric</th>
                          <th className="py-2 px-3 text-blue-700">PSO</th>
                          <th className="py-2 px-3 text-purple-700">GA</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        <tr>
                          <td className="py-2 px-3 font-medium text-gray-600">Best Fitness</td>
                          <td className="py-2 px-3 font-mono font-bold text-blue-700">
                            {optimizerResults.case_N2.pso.best_fitness.toFixed(4)}
                          </td>
                          <td className="py-2 px-3 font-mono font-bold text-purple-700">
                            {optimizerResults.case_N2.ga.best_fitness.toFixed(4)}
                          </td>
                        </tr>
                        <tr>
                          <td className="py-2 px-3 font-medium text-gray-600">Voltage Violations</td>
                          <td className="py-2 px-3 font-semibold text-emerald-700">
                            {optimizerResults.case_N2.pso.num_violations}
                          </td>
                          <td className="py-2 px-3 font-semibold text-emerald-700">
                            {optimizerResults.case_N2.ga.num_violations}
                          </td>
                        </tr>
                        <tr>
                          <td className="py-2 px-3 font-medium text-gray-600">Computation Time</td>
                          <td className="py-2 px-3 text-gray-700">
                            {optimizerResults.case_N2.pso.time_seconds.toFixed(2)}s
                          </td>
                          <td className="py-2 px-3 text-gray-700">
                            {optimizerResults.case_N2.ga.time_seconds.toFixed(2)}s
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  {/* Line Chart */}
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={buildChartData(optimizerResults.case_N2)}
                        margin={{ top: 10, right: 20, left: 0, bottom: 0 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis
                          dataKey="iteration"
                          stroke="#888888"
                          fontSize={11}
                          tickLine={false}
                          label={{ value: "Iteration / Gen", position: "insideBottomRight", offset: -5, fontSize: 10 }}
                        />
                        <YAxis stroke="#888888" fontSize={11} tickLine={false} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "#ffffff",
                            borderRadius: "8px",
                            boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                            fontSize: "12px",
                          }}
                        />
                        <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }} />
                        <Line
                          type="monotone"
                          dataKey="PSO"
                          stroke="#2563eb"
                          strokeWidth={2.5}
                          dot={false}
                          activeDot={{ r: 5 }}
                        />
                        <Line
                          type="monotone"
                          dataKey="GA"
                          stroke="#9333ea"
                          strokeWidth={2}
                          strokeDasharray="4 4"
                          dot={false}
                          activeDot={{ r: 5 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Plain-Language Interpretation */}
                <div className="mt-4 p-3.5 bg-blue-50/70 border border-blue-100 rounded-xl text-xs text-blue-900">
                  💡 <strong>Analysis:</strong>{" "}
                  {generateInterpretation(
                    optimizerResults.case_N2.pso,
                    optimizerResults.case_N2.ga,
                    "N=2"
                  )}
                </div>
              </div>
            )}

            {/* Case N=10 Locations */}
            {optimizerResults.case_N10 && (
              <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between border-b border-gray-100 pb-3 mb-4">
                    <h3 className="text-lg font-bold text-gray-900">
                      Comparison: N=10 Center Locations
                    </h3>
                    <span className="text-xs px-2.5 py-1 bg-purple-100 text-purple-800 font-semibold rounded-full">
                      Full System Benchmark
                    </span>
                  </div>

                  {/* Summary Comparison Table */}
                  <div className="overflow-x-auto mb-6">
                    <table className="w-full text-xs text-left border border-gray-200 rounded-lg overflow-hidden">
                      <thead className="bg-gray-50 text-gray-600 uppercase font-semibold">
                        <tr>
                          <th className="py-2 px-3">Metric</th>
                          <th className="py-2 px-3 text-blue-700">PSO</th>
                          <th className="py-2 px-3 text-purple-700">GA</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        <tr>
                          <td className="py-2 px-3 font-medium text-gray-600">Best Fitness</td>
                          <td className="py-2 px-3 font-mono font-bold text-blue-700">
                            {optimizerResults.case_N10.pso.best_fitness.toFixed(4)}
                          </td>
                          <td className="py-2 px-3 font-mono font-bold text-purple-700">
                            {optimizerResults.case_N10.ga.best_fitness.toFixed(4)}
                          </td>
                        </tr>
                        <tr>
                          <td className="py-2 px-3 font-medium text-gray-600">Voltage Violations</td>
                          <td className="py-2 px-3 font-semibold text-amber-700">
                            {optimizerResults.case_N10.pso.num_violations}
                          </td>
                          <td className="py-2 px-3 font-semibold text-red-700">
                            {optimizerResults.case_N10.ga.num_violations}
                          </td>
                        </tr>
                        <tr>
                          <td className="py-2 px-3 font-medium text-gray-600">Computation Time</td>
                          <td className="py-2 px-3 text-gray-700">
                            {optimizerResults.case_N10.pso.time_seconds.toFixed(2)}s
                          </td>
                          <td className="py-2 px-3 text-gray-700">
                            {optimizerResults.case_N10.ga.time_seconds.toFixed(2)}s
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  {/* Line Chart */}
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={buildChartData(optimizerResults.case_N10)}
                        margin={{ top: 10, right: 20, left: 0, bottom: 0 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis
                          dataKey="iteration"
                          stroke="#888888"
                          fontSize={11}
                          tickLine={false}
                          label={{ value: "Iteration / Gen", position: "insideBottomRight", offset: -5, fontSize: 10 }}
                        />
                        <YAxis stroke="#888888" fontSize={11} tickLine={false} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "#ffffff",
                            borderRadius: "8px",
                            boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                            fontSize: "12px",
                          }}
                        />
                        <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }} />
                        <Line
                          type="monotone"
                          dataKey="PSO"
                          stroke="#2563eb"
                          strokeWidth={2.5}
                          dot={false}
                          activeDot={{ r: 5 }}
                        />
                        <Line
                          type="monotone"
                          dataKey="GA"
                          stroke="#9333ea"
                          strokeWidth={2}
                          strokeDasharray="4 4"
                          dot={false}
                          activeDot={{ r: 5 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Plain-Language Interpretation */}
                <div className="mt-4 p-3.5 bg-purple-50/70 border border-purple-100 rounded-xl text-xs text-purple-900">
                  💡 <strong>Analysis:</strong>{" "}
                  {generateInterpretation(
                    optimizerResults.case_N10.pso,
                    optimizerResults.case_N10.ga,
                    "N=10"
                  )}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="p-8 bg-white border border-gray-200 rounded-2xl text-center text-gray-500 text-sm">
            No optimizer benchmark data available.
          </div>
        )}
      </section>
    </div>
  );
}
