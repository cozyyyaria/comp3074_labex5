package com.example.gpslocationtracker

import android.Manifest
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.example.gpslocationtracker.databinding.ActivityMainBinding

/**
 * MainActivity handles:
 * 1. Runtime permission checking and requesting for ACCESS_FINE_LOCATION and ACCESS_COARSE_LOCATION.
 * 2. GPS hardware status checks (LocationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)).
 * 3. Continuous and on-demand location updates from GPS hardware via LocationManager and LocationListener.
 * 4. Real-time UI updates for latitude, longitude, altitude, accuracy, speed, and timestamps.
 */
class MainActivity : AppCompatActivity(), LocationListener {

    private lateinit var binding: ActivityMainBinding
    private lateinit var locationManager: LocationManager

    private var isTracking: Boolean = false
    private var lastKnownLocation: Location? = null

    // Register Activity Result Launcher for Location Permissions
    private val locationPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val fineLocationGranted = permissions[Manifest.permission.ACCESS_FINE_LOCATION] ?: false
        val coarseLocationGranted = permissions[Manifest.permission.ACCESS_COARSE_LOCATION] ?: false

        if (fineLocationGranted) {
            // Fine Location is granted; GPS hardware can now be accessed
            binding.bannerPermission.visibility = View.GONE
            Toast.makeText(this, "GPS Location permission granted", Toast.LENGTH_SHORT).show()
            checkGpsAndStartTracking()
        } else if (coarseLocationGranted) {
            // Only coarse location granted (insufficient for high precision GPS)
            binding.bannerPermission.visibility = View.VISIBLE
            showFineLocationRationaleDialog()
        } else {
            // Permission denied
            binding.bannerPermission.visibility = View.VISIBLE
            updateStatusUi(GpsState.PERMISSION_REQUIRED)
            Toast.makeText(this, R.string.msg_permission_denied, Toast.LENGTH_LONG).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        locationManager = getSystemService(Context.LOCATION_SERVICE) as LocationManager

        setupClickListeners()
    }

    override fun onResume() {
        super.onResume()
        // Refresh UI state based on current permissions and device settings
        refreshState()
    }

    override fun onPause() {
        super.onPause()
        // Pause GPS updates when app is in background to conserve battery
        if (isTracking) {
            stopLocationUpdates()
            isTracking = false
            updateTrackingButtonState()
        }
    }

    private fun setupClickListeners() {
        // Toggle continuous GPS tracking
        binding.btnToggleTracking.setOnClickListener {
            if (isTracking) {
                stopLocationUpdates()
                isTracking = false
                updateStatusUi(GpsState.READY)
                updateTrackingButtonState()
            } else {
                requestLocationAndStart()
            }
        }

        // On-demand one-time location refresh
        binding.btnRefreshLocation.setOnClickListener {
            requestSingleLocationFix()
        }

        // Copy coordinates to system clipboard
        binding.btnCopyCoords.setOnClickListener {
            copyCoordinatesToClipboard()
        }

        // Open current coordinates in Google Maps or external map app
        binding.btnOpenMap.setOnClickListener {
            openCoordinatesInMaps()
        }

        // Banner button to grant permission
        binding.btnGrantPermission.setOnClickListener {
            requestLocationPermissions()
        }

        // Banner button to open device location settings
        binding.btnEnableGps.setOnClickListener {
            val intent = Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS)
            startActivity(intent)
        }
    }

    private fun refreshState() {
        if (!LocationUtils.hasLocationPermission(this)) {
            binding.bannerPermission.visibility = View.VISIBLE
            binding.bannerGpsDisabled.visibility = View.GONE
            updateStatusUi(GpsState.PERMISSION_REQUIRED)
        } else {
            binding.bannerPermission.visibility = View.GONE
            if (!LocationUtils.isGpsProviderEnabled(this)) {
                binding.bannerGpsDisabled.visibility = View.VISIBLE
                updateStatusUi(GpsState.GPS_DISABLED)
            } else {
                binding.bannerGpsDisabled.visibility = View.GONE
                if (!isTracking && lastKnownLocation == null) {
                    fetchLastKnownGpsLocation()
                }
            }
        }
    }

    /**
     * Verifies permissions and GPS provider state before starting continuous tracking.
     */
    private fun requestLocationAndStart() {
        if (!LocationUtils.hasLocationPermission(this)) {
            requestLocationPermissions()
            return
        }

        checkGpsAndStartTracking()
    }

    private fun checkGpsAndStartTracking() {
        if (!LocationUtils.isGpsProviderEnabled(this)) {
            showEnableGpsDialog()
            binding.bannerGpsDisabled.visibility = View.VISIBLE
            updateStatusUi(GpsState.GPS_DISABLED)
            return
        }

        binding.bannerGpsDisabled.visibility = View.GONE
        startLocationUpdates()
    }

    /**
     * Registers GPS location listener for real-time satellite updates.
     */
    private fun startLocationUpdates() {
        if (!LocationUtils.hasLocationPermission(this)) return

        try {
            updateStatusUi(GpsState.ACQUIRING)
            isTracking = true
            updateTrackingButtonState()

            // Request updates from GPS_PROVIDER:
            // minTimeMs = 1000 ms (1 second), minDistanceM = 0 meters (report every change)
            locationManager.requestLocationUpdates(
                LocationManager.GPS_PROVIDER,
                1000L,
                0f,
                this
            )

            // Also read last known location for instant display while satellites lock
            fetchLastKnownGpsLocation()
        } catch (e: SecurityException) {
            e.printStackTrace()
            Toast.makeText(this, "Security Exception: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    /**
     * Unregisters location listener to conserve device battery.
     */
    private fun stopLocationUpdates() {
        try {
            locationManager.removeUpdates(this)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    /**
     * Requests a single high-accuracy location fix.
     */
    private fun requestSingleLocationFix() {
        if (!LocationUtils.hasLocationPermission(this)) {
            requestLocationPermissions()
            return
        }

        if (!LocationUtils.isGpsProviderEnabled(this)) {
            showEnableGpsDialog()
            return
        }

        updateStatusUi(GpsState.ACQUIRING)
        Toast.makeText(this, "Acquiring satellite fix…", Toast.LENGTH_SHORT).show()

        try {
            fetchLastKnownGpsLocation()
            locationManager.requestSingleUpdate(LocationManager.GPS_PROVIDER, this, null)
        } catch (e: SecurityException) {
            e.printStackTrace()
        }
    }

    /**
     * Queries the most recent cached GPS fix.
     */
    private fun fetchLastKnownGpsLocation() {
        if (!LocationUtils.hasLocationPermission(this)) return

        try {
            val location = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER)
                ?: locationManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER)

            if (location != null) {
                updateLocationUi(location)
            }
        } catch (e: SecurityException) {
            e.printStackTrace()
        }
    }

    /**
     * Callback when a new GPS location is acquired.
     */
    override fun onLocationChanged(location: Location) {
        lastKnownLocation = location
        updateLocationUi(location)
        updateStatusUi(GpsState.ACTIVE)
    }

    override fun onProviderEnabled(provider: String) {
        if (provider == LocationManager.GPS_PROVIDER) {
            binding.bannerGpsDisabled.visibility = View.GONE
            Toast.makeText(this, "GPS hardware enabled", Toast.LENGTH_SHORT).show()
            if (isTracking) {
                startLocationUpdates()
            }
        }
    }

    override fun onProviderDisabled(provider: String) {
        if (provider == LocationManager.GPS_PROVIDER) {
            binding.bannerGpsDisabled.visibility = View.VISIBLE
            updateStatusUi(GpsState.GPS_DISABLED)
            Toast.makeText(this, "GPS hardware was disabled", Toast.LENGTH_SHORT).show()
        }
    }

    @Deprecated("Deprecated in Android Q")
    override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {
        // Maintained for backward compatibility across older Android SDKs
    }

    /**
     * Populates the UI widgets with newly acquired GPS telemetry.
     */
    private fun updateLocationUi(location: Location) {
        val lat = location.latitude
        val lng = location.longitude

        binding.tvLatitude.text = LocationUtils.formatLatitude(lat)
        binding.tvLongitude.text = LocationUtils.formatLongitude(lng)

        binding.tvLatitudeDms.text = LocationUtils.toDms(lat, isLatitude = true)
        binding.tvLongitudeDms.text = LocationUtils.toDms(lng, isLatitude = false)

        binding.tvAltitude.text = LocationUtils.formatAltitude(location)
        binding.tvAccuracy.text = LocationUtils.formatAccuracy(location)
        binding.tvSpeed.text = LocationUtils.formatSpeed(location)
        binding.tvProvider.text = location.provider?.uppercase() ?: "GPS"
        binding.tvLastFix.text = LocationUtils.formatTimestamp(location.time)
    }

    /**
     * Updates top status pill reflecting active GPS receiver state.
     */
    private fun updateStatusUi(state: GpsState) {
        when (state) {
            GpsState.ACTIVE -> {
                binding.tvStatusBadge.text = getString(R.string.status_active)
                binding.tvStatusBadge.setBackgroundResource(R.drawable.badge_status_active)
                binding.tvStatusBadge.setTextColor(ContextCompat.getColor(this, R.color.gps_active))
            }
            GpsState.ACQUIRING -> {
                binding.tvStatusBadge.text = getString(R.string.status_acquiring)
                binding.tvStatusBadge.setBackgroundResource(R.drawable.badge_status_searching)
                binding.tvStatusBadge.setTextColor(ContextCompat.getColor(this, R.color.gps_searching))
            }
            GpsState.READY -> {
                binding.tvStatusBadge.text = getString(R.string.status_ready)
                binding.tvStatusBadge.setBackgroundResource(R.drawable.badge_status_searching)
                binding.tvStatusBadge.setTextColor(ContextCompat.getColor(this, R.color.gps_searching))
            }
            GpsState.GPS_DISABLED -> {
                binding.tvStatusBadge.text = getString(R.string.status_gps_disabled)
                binding.tvStatusBadge.setBackgroundResource(R.drawable.badge_status_disabled)
                binding.tvStatusBadge.setTextColor(ContextCompat.getColor(this, R.color.gps_error))
            }
            GpsState.PERMISSION_REQUIRED -> {
                binding.tvStatusBadge.text = getString(R.string.status_permission_required)
                binding.tvStatusBadge.setBackgroundResource(R.drawable.badge_status_disabled)
                binding.tvStatusBadge.setTextColor(ContextCompat.getColor(this, R.color.gps_error))
            }
        }
    }

    private fun updateTrackingButtonState() {
        if (isTracking) {
            binding.btnToggleTracking.text = getString(R.string.btn_stop_tracking)
            binding.btnToggleTracking.setBackgroundColor(ContextCompat.getColor(this, R.color.gps_error))
        } else {
            binding.btnToggleTracking.text = getString(R.string.btn_start_tracking)
            binding.btnToggleTracking.setBackgroundColor(ContextCompat.getColor(this, R.color.primary))
        }
    }

    private fun copyCoordinatesToClipboard() {
        val location = lastKnownLocation
        if (location == null) {
            Toast.makeText(this, "No location fix available yet to copy", Toast.LENGTH_SHORT).show()
            return
        }

        val text = "${location.latitude}, ${location.longitude}"
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = ClipData.newPlainText("GPS Coordinates", text)
        clipboard.setPrimaryClip(clip)

        Toast.makeText(this, getString(R.string.msg_coords_copied), Toast.LENGTH_SHORT).show()
    }

    private fun openCoordinatesInMaps() {
        val location = lastKnownLocation
        if (location == null) {
            Toast.makeText(this, "Acquire GPS fix first to view on map", Toast.LENGTH_SHORT).show()
            return
        }

        val uri = Uri.parse("geo:${location.latitude},${location.longitude}?q=${location.latitude},${location.longitude}(Current+GPS+Location)")
        val mapIntent = Intent(Intent.ACTION_VIEW, uri)
        if (mapIntent.resolveActivity(packageManager) != null) {
            startActivity(mapIntent)
        } else {
            // Fallback to web browser Google Maps
            val webUri = Uri.parse("https://www.google.com/maps/search/?api=1&query=${location.latitude},${location.longitude}")
            startActivity(Intent(Intent.ACTION_VIEW, webUri))
        }
    }

    /**
     * Prompts Android runtime permission dialog for Fine and Coarse location.
     */
    private fun requestLocationPermissions() {
        locationPermissionLauncher.launch(
            arrayOf(
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION
            )
        )
    }

    private fun showFineLocationRationaleDialog() {
        AlertDialog.Builder(this)
            .setTitle("Precise GPS Required")
            .setMessage("This application requires 'Precise' (Fine) location permission to read direct satellite telemetry.")
            .setPositiveButton("Grant") { _, _ -> requestLocationPermissions() }
            .setNegativeButton(R.string.dialog_cancel, null)
            .show()
    }

    private fun showEnableGpsDialog() {
        AlertDialog.Builder(this)
            .setTitle(R.string.status_gps_disabled)
            .setMessage(R.string.msg_gps_disabled)
            .setPositiveButton(R.string.dialog_settings) { _, _ ->
                startActivity(Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS))
            }
            .setNegativeButton(R.string.dialog_cancel, null)
            .show()
    }

    enum class GpsState {
        READY,
        ACQUIRING,
        ACTIVE,
        GPS_DISABLED,
        PERMISSION_REQUIRED
    }
}

