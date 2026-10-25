package com.example.gpslocationtracker

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationManager
import androidx.core.content.ContextCompat
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlin.math.abs

/**
 * Utility functions for GPS coordinates formatting, unit conversions,
 * and permission checks.
 */
object LocationUtils {

    /**
     * Checks whether both fine and coarse location permissions have been granted.
     */
    fun hasLocationPermission(context: Context): Boolean {
        val fineLocation = ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED

        val coarseLocation = ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED

        return fineLocation && coarseLocation
    }

    /**
     * Checks if the device's GPS hardware provider is enabled.
     */
    fun isGpsProviderEnabled(context: Context): Boolean {
        val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as? LocationManager
        return locationManager?.isProviderEnabled(LocationManager.GPS_PROVIDER) == true
    }

    /**
     * Formats latitude with cardinal direction (N/S).
     */
    fun formatLatitude(latitude: Double): String {
        val direction = if (latitude >= 0) "N" else "S"
        return String.format(Locale.US, "%.6f° %s", abs(latitude), direction)
    }

    /**
     * Formats longitude with cardinal direction (E/W).
     */
    fun formatLongitude(longitude: Double): String {
        val direction = if (longitude >= 0) "E" else "W"
        return String.format(Locale.US, "%.6f° %s", abs(longitude), direction)
    }

    /**
     * Converts a decimal coordinate into Degrees, Minutes, Seconds (DMS) string.
     */
    fun toDms(coordinate: Double, isLatitude: Boolean): String {
        val direction = if (isLatitude) {
            if (coordinate >= 0) "N" else "S"
        } else {
            if (coordinate >= 0) "E" else "W"
        }

        val absVal = abs(coordinate)
        val degrees = absVal.toInt()
        val minutesDouble = (absVal - degrees) * 60.0
        val minutes = minutesDouble.toInt()
        val seconds = (minutesDouble - minutes) * 60.0

        return String.format(Locale.US, "%d° %02d' %04.1f\" %s", degrees, minutes, seconds, direction)
    }

    /**
     * Formats altitude in both meters and feet.
     */
    fun formatAltitude(location: Location): String {
        return if (location.hasAltitude()) {
            val meters = location.altitude
            val feet = meters * 3.28084
            String.format(Locale.US, "%.1f m (%.0f ft)", meters, feet)
        } else {
            "N/A"
        }
    }

    /**
     * Formats accuracy with metric precision.
     */
    fun formatAccuracy(location: Location): String {
        return if (location.hasAccuracy()) {
            String.format(Locale.US, "± %.1f m", location.accuracy)
        } else {
            "Unknown"
        }
    }

    /**
     * Formats speed in km/h and mph.
     */
    fun formatSpeed(location: Location): String {
        return if (location.hasSpeed()) {
            val speedMps = location.speed
            val speedKmh = speedMps * 3.6
            val speedMph = speedMps * 2.23694
            String.format(Locale.US, "%.1f km/h (%.1f mph)", speedKmh, speedMph)
        } else {
            "0.0 km/h (Stationary)"
        }
    }

    /**
     * Formats timestamp to readable local time string.
     */
    fun formatTimestamp(timeMs: Long): String {
        val sdf = SimpleDateFormat("yyyy-MM-dd HH:mm:ss z", Locale.getDefault())
        return sdf.format(Date(timeMs))
    }
}

