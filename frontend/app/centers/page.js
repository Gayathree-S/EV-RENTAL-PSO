"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "../lib/api";
import { getStoredUser } from "../lib/auth";

export default function CentersPage() {
  const router = useRouter();
  const [centers, setCenters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [user, setUser] = useState(null);

  useEffect(() => {
    const storedUser = getStoredUser();
    if (!storedUser) {
      router.push("/login");
      return;
    }
    setUser(storedUser);

    const fetchCenters = async () => {
      try {
        setLoading(true);
        const data = await api.get("/centers");
        setCenters(data);
      } catch (err) {
        setError(err.message || "Failed to load rental centers.");
      } finally {
        setLoading(false);
      }
    };

    fetchCenters();
  }, [router]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <div className="w-10 h-10 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin"></div>
        <p className="mt-4 text-sm text-gray-500">Loading grid-optimized rental centers...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto my-12 p-6 bg-red-50 border border-red-200 rounded-2xl text-center">
        <h2 className="text-lg font-bold text-red-800">Error Loading Centers</h2>
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

  const totalVehicles = centers.reduce((acc, c) => acc + (c.vehicles ? c.vehicles.length : 0), 0);
  const availableVehicles = centers.reduce(
    (acc, c) => acc + (c.vehicles ? c.vehicles.filter((v) => v.is_available).length : 0),
    0
  );

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
            Rental Centers & Fleet Inventory
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Browse grid-optimized EV rental centers positioned by Particle Swarm Optimization (PSO)
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 bg-emerald-50 border border-emerald-200 rounded-xl text-center">
            <span className="text-xs font-semibold text-emerald-800 uppercase tracking-wider block">
              Available
            </span>
            <span className="text-lg font-bold text-emerald-700">
              {availableVehicles} / {totalVehicles} EVs
            </span>
          </div>
          <div className="px-4 py-2 bg-blue-50 border border-blue-200 rounded-xl text-center">
            <span className="text-xs font-semibold text-blue-800 uppercase tracking-wider block">
              Total Hubs
            </span>
            <span className="text-lg font-bold text-blue-700">{centers.length} Centers</span>
          </div>
        </div>
      </div>

      {/* Centers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {centers.map((center) => {
          const centerAvailable = center.vehicles.filter((v) => v.is_available).length;
          return (
            <div
              key={center.id}
              className="bg-white rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between overflow-hidden"
            >
              <div className="p-6 border-b border-gray-100 bg-gradient-to-br from-gray-50 to-white">
                <div className="flex items-center justify-between">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                    Bus #{center.bus_number}
                  </span>
                  <span className="text-xs font-medium text-gray-500">
                    Allocated Cap: <strong className="text-gray-900">{center.max_fleet_size} EVs</strong>
                  </span>
                </div>
                <h2 className="text-lg font-bold text-gray-900 mt-2">{center.name}</h2>
                <p className="text-xs text-gray-500 mt-0.5">
                  Modified IEEE 33-Bus Radial Grid Node
                </p>
              </div>

              <div className="p-6 flex-1 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-bold text-gray-600 uppercase tracking-wider">
                      Fleet Vehicles ({centerAvailable} Available)
                    </span>
                  </div>

                  {center.vehicles.length === 0 ? (
                    <div className="col-span-2 py-6 text-center text-xs text-gray-400">
                      No vehicles assigned to this center.
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 gap-2">
                      {center.vehicles.map((v) => (
                        <div key={v.id}>
                          {v.is_available ? (
                            <Link
                              href={`/book/${v.id}`}
                              className="block p-3 rounded-xl border border-emerald-200 bg-emerald-50/50 hover:bg-emerald-100 hover:border-emerald-300 transition-all text-center group cursor-pointer"
                            >
                              <span className="text-xs font-mono font-bold text-emerald-900 block">
                                {v.vehicle_code}
                              </span>
                              <span className="text-[10px] font-semibold text-emerald-700 mt-1 inline-flex items-center gap-1 group-hover:underline">
                                <span>●</span> Book Now &rarr;
                              </span>
                            </Link>
                          ) : (
                            <div className="p-3 rounded-xl border border-gray-200 bg-gray-100/70 text-center opacity-70 cursor-not-allowed">
                              <span className="text-xs font-mono font-medium text-gray-500 block">
                                {v.vehicle_code}
                              </span>
                              <span className="text-[10px] font-semibold text-gray-400 mt-1 block">
                                Reserved
                              </span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  {center.vehicles.length > 0 && centerAvailable === 0 && (
                    <div className="mt-3 text-center text-xs text-amber-600 font-medium py-1 px-3 bg-amber-50 rounded-lg border border-amber-100">
                      All vehicles currently reserved — check back later
                    </div>
                  )}
                </div>

                <div className="mt-6 pt-4 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
                  <span>Center ID #{center.id}</span>
                  {centerAvailable > 0 ? (
                    <span className="text-emerald-600 font-medium">Click vehicle to book</span>
                  ) : (
                    <span className="text-amber-600 font-medium">Fully reserved</span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
