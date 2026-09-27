"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";
import { getStoredUser } from "../../lib/auth";

export default function BookVehiclePage({ params }) {
  const unwrappedParams = use(params);
  const vehicleId = parseInt(unwrappedParams.vehicleId, 10);
  const router = useRouter();

  const [user, setUser] = useState(null);
  const [formData, setFormData] = useState({
    dropoff_time_hr: 9,   // Default 09:00
    pickup_time_hr: 18,    // Default 18:00
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [bookingResult, setBookingResult] = useState(null);

  useEffect(() => {
    const storedUser = getStoredUser();
    if (!storedUser) {
      router.push("/login");
      return;
    }
    setUser(storedUser);
  }, [router]);

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: parseFloat(e.target.value),
    }));
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!user) return;
    setError("");
    setLoading(true);

    try {
      const payload = {
        user_id: user.user_id,
        vehicle_id: vehicleId,
        dropoff_time_hr: formData.dropoff_time_hr,
        pickup_time_hr: formData.pickup_time_hr,
      };

      const result = await api.post("/bookings", payload);
      setBookingResult(result);
    } catch (err) {
      setError(err.message || "Failed to complete vehicle booking.");
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div className="max-w-xl mx-auto my-8">
      <div className="mb-4">
        <Link
          href="/centers"
          className="text-sm font-medium text-emerald-600 hover:text-emerald-700 flex items-center gap-1"
        >
          &larr; Back to Rental Centers
        </Link>
      </div>

      <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-200">
        <div className="border-b border-gray-100 pb-5 mb-6">
          <span className="inline-block px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 mb-2">
            Vehicle ID #{vehicleId}
          </span>
          <h1 className="text-2xl font-extrabold text-gray-900">
            Book Electric Vehicle
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Specify your rental schedule. The system will use machine learning to forecast the required charging energy.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700">
            <strong>Booking Error:</strong> {error}
          </div>
        )}

        {bookingResult ? (
          <div className="space-y-6">
            <div className="p-6 rounded-2xl bg-emerald-50 border border-emerald-200 text-center">
              <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto text-2xl mb-3">
                ✓
              </div>
              <h2 className="text-xl font-bold text-emerald-900">
                Booking Confirmed!
              </h2>
              <p className="text-sm text-emerald-700 mt-1">
                Your reservation for vehicle{" "}
                <strong className="font-mono">{bookingResult.vehicle?.vehicle_code || `EV #${vehicleId}`}</strong>{" "}
                has been successfully placed.
              </p>
            </div>

            {/* ML Prediction Result Banner */}
            <div className="p-5 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-700 text-white shadow-md">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs uppercase tracking-wider text-emerald-100 font-semibold block">
                    AI Demand Forecast Result
                  </span>
                  <p className="text-xs text-emerald-200 mt-0.5">
                    Predicted via Random Forest Regressor (Task 7)
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-2xl sm:text-3xl font-extrabold">
                    {bookingResult.predicted_charging_energy_kwh != null
                      ? `${bookingResult.predicted_charging_energy_kwh.toFixed(2)} kWh`
                      : "N/A"}
                  </span>
                  <span className="text-xs text-emerald-100 block">
                    Estimated Charging Demand
                  </span>
                </div>
              </div>
            </div>

            {/* Booking Details Summary */}
            <div className="bg-gray-50 rounded-xl p-4 border border-gray-200 text-sm space-y-2">
              <div className="flex justify-between text-gray-600">
                <span>Booking Reference:</span>
                <strong className="text-gray-900">#{bookingResult.id}</strong>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>Renter:</span>
                <strong className="text-gray-900">{bookingResult.user?.name || user.name}</strong>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>Pickup Time:</span>
                <strong className="text-gray-900">{bookingResult.dropoff_time_hr}:00</strong>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>Return Time:</span>
                <strong className="text-gray-900">{bookingResult.pickup_time_hr}:00</strong>
              </div>
            </div>

            <div className="flex gap-3">
              <Link
                href="/centers"
                className="flex-1 py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-sm transition-colors text-center shadow-sm"
              >
                Return to Centers
              </Link>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Pickup Hour (0 – 23)
              </label>
              <input
                type="number"
                name="dropoff_time_hr"
                min="0"
                max="23"
                step="0.5"
                required
                value={formData.dropoff_time_hr}
                onChange={handleChange}
                className="w-full px-3.5 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm"
              />
              <p className="text-xs text-gray-500 mt-1">
                Hour of the day when you will pick up the vehicle (e.g. 9.0 = 9:00 AM, 14.5 = 2:30 PM).
              </p>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Return Hour (0 – 23)
              </label>
              <input
                type="number"
                name="pickup_time_hr"
                min="0"
                max="23"
                step="0.5"
                required
                value={formData.pickup_time_hr}
                onChange={handleChange}
                className="w-full px-3.5 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm"
              />
              <p className="text-xs text-gray-500 mt-1">
                Hour of the day when you will return the vehicle to the rental hub.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-emerald-50/70 border border-emerald-100 text-xs text-emerald-800">
              💡 <strong>Smart Charging Integration:</strong> Your rental window is fed into our trained machine learning model to estimate the total battery charging energy (kWh) needed upon return.
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm transition-colors shadow-md disabled:opacity-60 cursor-pointer"
            >
              {loading ? "Calculating Demand & Confirming..." : "Confirm Booking"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
