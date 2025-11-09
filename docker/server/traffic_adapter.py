"""
Traffic Adapter for SAGSIN Simulator - TRANSFORM MODE
======================================================
Transforms ANY simulator traffic into realistic dataset-matching metrics

Philosophy:
    Simulator: SIMPLE traffic counting (any amount)
              ↓
    Adapter:   TRANSFORM to realistic patterns
              ↓
    Output:    ALWAYS matches dataset distribution

Key Features:
- Independent of simulator complexity
- Calibrated with real dataset statistics
- Proper temporal patterns (hourly/weekly cycles)
- Correlated metrics (util ↔ loss ↔ jitter ↔ RTT)
- Link-type specific behaviors

Author: PBL4 Team
Date: 2025-11-08 (Refactored to Transform approach)
"""

import numpy as np
import math
from datetime import datetime

# Set seed for reproducibility
REPRODUCIBILITY_SEED = 42
np.random.seed(REPRODUCIBILITY_SEED)


class TrafficAdapter:
    """
    Transform simulator traffic to realistic SAGSIN metrics
    
    Method: Statistical calibration with dataset
    - Takes RAW traffic count from simulator (any amount)
    - Applies temporal patterns (time of day, day of week)
    - Scales to match dataset distribution
    - Ensures proper correlations between metrics
    
    Output: Realistic metrics ready for ML prediction
    """
    
    # ============================================
    # LINK TYPE PROFILES (Calibrated from dataset)
    # ============================================
    # These profiles represent REALISTIC traffic patterns
    # observed in real SAGSIN network (from training data)
    LINK_PROFILES = {
        'space_ground': {
            # Utilization targets (from training: mean=0.333, median=0.317, max=0.48)
            'base_util': 0.33,          # Baseline: 33% (matches training mean)
            'util_std': 0.08,           # Low variation
            'util_peak': 0.45,          # Peak hours: 45%
            'util_night': 0.25,         # Night: 25%
            
            # Loss characteristics
            'loss_base': 0.002,         # 0.2% baseline
            'loss_high_util': 0.008,    # 0.8% at high utilization
            
            # Jitter
            'jitter_base': 15,          # 15ms baseline
            'jitter_max': 80,           # 80ms at congestion
            
            # Temporal behavior
            'peak_factor': 1.15,        # 15% increase in peak
            'weekend_factor': 0.90,     # 10% decrease weekend
            
            # Traffic volume (bytes per second) - matched to training bitrate ~10 Mbps
            'bytes_per_sec_mean': 1_250_000,    # ~10 Mbps average (training mean)
            'bytes_per_sec_peak': 1_875_000,    # ~15 Mbps peak
            
            'description': 'SATELLITE → GROUND: Stable, moderate traffic (capacity 25-35 Mbps)'
        },
        'space_air': {
            # Training: mean=0.523, median=0.745, max=0.926 - HIGH utilization with peaks!
            'base_util': 0.52,          # Baseline: 52% (training mean)
            'util_std': 0.25,           # High variation
            'util_peak': 0.85,          # Peak: 85%
            'util_night': 0.15,         # UAVs land at night
            
            'loss_base': 0.003,
            'loss_high_util': 0.012,
            
            'jitter_base': 20,
            'jitter_max': 100,
            
            'peak_factor': 1.6,         # Strong peaks
            'weekend_factor': 1.0,
            
            # Training bitrate: mean=7 Mbps, median=10 Mbps (capacity 12-15 Mbps)
            'bytes_per_sec_mean': 875_000,      # ~7 Mbps average
            'bytes_per_sec_peak': 1_375_000,    # ~11 Mbps peak
            
            'description': 'SATELLITE → UAV: HIGH utilization with peaks (capacity 12-15 Mbps)'
        },
        'air_ground': {
            # Training: mean=0.536, median=0.655, max=0.98 - VERY HIGH traffic!
            'base_util': 0.54,          # Baseline: 54% (training mean)
            'util_std': 0.20,           # Moderate variation
            'util_peak': 0.85,          # Peak: 85%
            'util_night': 0.25,         # Still active at night
            
            'loss_base': 0.001,
            'loss_high_util': 0.005,
            
            'jitter_base': 8,
            'jitter_max': 60,
            
            'peak_factor': 1.5,         # Moderate peaks
            'weekend_factor': 0.55,     # Much lower on weekend
            
            # Training bitrate: mean=29 Mbps, median=36 Mbps (capacity 50-60 Mbps)
            'bytes_per_sec_mean': 3_625_000,    # ~29 Mbps average (training mean)
            'bytes_per_sec_peak': 5_625_000,    # ~45 Mbps peak
            
            'description': 'UAV → GROUND: VERY HIGH TRAFFIC (capacity 50-60 Mbps)'
        },
        'space_space': {
            # Training: mean=0.300, median=0.300, max=0.336 - VERY STABLE!
            'base_util': 0.30,          # Baseline: 30% (training mean, very consistent)
            'util_std': 0.02,           # Very low variation
            'util_peak': 0.33,          # Peak: 33%
            'util_night': 0.30,         # Constant 24/7
            
            'loss_base': 0.0002,
            'loss_high_util': 0.001,
            
            'jitter_base': 3,
            'jitter_max': 15,
            
            'peak_factor': 1.0,         # No temporal pattern
            'weekend_factor': 1.0,
            
            # Training bitrate: mean=3.0 Mbps (capacity 10 Mbps)
            'bytes_per_sec_mean': 375_000,      # ~3.0 Mbps (training mean)
            'bytes_per_sec_peak': 420_000,      # ~3.36 Mbps (training max)
            
            'description': 'SATELLITE ↔ SATELLITE: Very stable (capacity 10 Mbps)'
        },
        'ground_sea': {
            # Training: mean=0.401, median=0.371, max=0.636
            'base_util': 0.40,          # Baseline: 40% (training mean)
            'util_std': 0.12,           # Moderate variation
            'util_peak': 0.58,          # Peak: 58%
            'util_night': 0.32,         # Lower at night
            
            'loss_base': 0.008,
            'loss_high_util': 0.025,
            
            'jitter_base': 25,
            'jitter_max': 150,
            
            'peak_factor': 1.3,
            'weekend_factor': 1.0,
            
            # Training bitrate: mean=2.4 Mbps, median=2.2 Mbps (capacity 6 Mbps)
            'bytes_per_sec_mean': 300_000,      # ~2.4 Mbps (training mean)
            'bytes_per_sec_peak': 475_000,      # ~3.8 Mbps peak
            
            'description': 'GROUND → SHIP: Moderate traffic, weather impact (capacity 6 Mbps)'
        },
        'default': {
            'base_util': 0.45,
            'util_std': 0.12,
            'util_peak': 0.70,
            'util_night': 0.15,
            
            'loss_base': 0.002,
            'loss_high_util': 0.008,
            
            'jitter_base': 10,
            'jitter_max': 80,
            
            'peak_factor': 1.5,
            'weekend_factor': 0.85,
            
            'bytes_per_sec_mean': 600_000,
            'bytes_per_sec_peak': 1_500_000,
            
            'description': 'Default profile for unknown link types'
        }
    }
    
    def __init__(self):
        """Initialize adapter in TRANSFORM mode"""
        print("=" * 70)
        print("✅ TrafficAdapter initialized - TRANSFORM MODE")
        print("=" * 70)
        print("📊 Method: Statistical calibration with dataset")
        print("🎯 Output: Realistic metrics independent of simulator")
        print("=" * 70)
    
    def get_link_profile(self, source_layer, destination_layer):
        """
        Get profile cho link type
        
        Args:
            source_layer: 'space', 'air', 'ground', 'sea'
            destination_layer: 'space', 'air', 'ground', 'sea'
        
        Returns:
            dict với base_util, util_variance, loss_base, etc.
        """
        link_type = f"{source_layer}_{destination_layer}"
        
        # Exact match
        if link_type in self.LINK_PROFILES:
            return self.LINK_PROFILES[link_type]
        
        # Reverse match (e.g. ground_space -> space_ground)
        reverse_type = f"{destination_layer}_{source_layer}"
        if reverse_type in self.LINK_PROFILES:
            return self.LINK_PROFILES[reverse_type]
        
        # Default
        print(f"   ℹ️  Using default profile for {link_type}")
        return self.LINK_PROFILES['default']
    
    def transform_traffic(self, raw_traffic, link):
        """
        🎯 CORE METHOD - Transform ANY simulator traffic to realistic metrics
        
        This is the KEY difference from aggregation approach:
        - Takes raw traffic count (ANY amount - even 0 bytes!)
        - Applies temporal patterns based on current time
        - Scales to match dataset distribution
        - Returns REALISTIC metrics matching training data
        
        Args:
            raw_traffic: dict with:
                - bytes_sent: int (from simulator, any amount)
                - duration: float (measurement window in seconds, typically 1.0)
            link: dict with link properties (same as generate_metrics)
        
        Returns:
            dict with ALL metrics matching dataset format
        
        Example:
            raw = {'bytes_sent': 5000, 'duration': 1.0}  # Small traffic
            metrics = adapter.transform_traffic(raw, link)
            # Output: bytes_sent ~400,000 (realistic for that time/link)
        """
        # Extract simulator input
        sim_bytes = raw_traffic.get('bytes_sent', 0)
        duration = raw_traffic.get('duration', 1.0)
        
        # Current time (LOCAL TIME)
        now = datetime.now()  
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        hour = now.hour
        day_of_week = now.weekday()
        is_weekend = day_of_week >= 5
        
        # Get link profile
        profile = self.get_link_profile(link['source_layer'], link['destination_layer'])
        link_type = f"{link['source_layer']}_{link['destination_layer']}"
        
        # ================================
        # STEP 1: TEMPORAL FACTORS
        # ================================
        # Calculate realistic utilization for THIS moment
        
        # 1.1 Hourly pattern (business hours, peak hours)
        if 'air_ground' in link_type.lower():
            # Strong business traffic peaks
            if 7 <= hour <= 9:
                hour_factor = 2.0  # Morning rush
            elif 12 <= hour <= 13:
                hour_factor = 1.3  # Lunch
            elif 17 <= hour <= 19:
                hour_factor = 2.2  # Evening peak
            elif 0 <= hour <= 6:
                hour_factor = 0.15  # Night (low)
            else:
                hour_factor = 1.0  # Normal hours
        
        elif 'space_air' in link_type.lower():
            # UAV daytime operation
            if 6 <= hour <= 20:
                hour_factor = profile['peak_factor']
            else:
                hour_factor = 0.1  # UAVs land at night
        
        elif link_type.lower() in ['space_ground', 'ground_sea']:
            # Moderate business hours effect
            if 8 <= hour <= 18:
                hour_factor = profile['peak_factor']
            else:
                hour_factor = 0.85
        
        else:
            # Satellite-satellite: no pattern
            hour_factor = 1.0
        
        # 1.2 Weekend factor
        week_factor = profile['weekend_factor'] if is_weekend else 1.0
        
        # 1.3 Calculate target utilization (what dataset shows at this time)
        if hour_factor > 1.5:
            # Peak hours
            target_util = profile['util_peak']
        elif hour_factor < 0.3:
            # Night hours
            target_util = profile['util_night']
        else:
            # Normal hours
            target_util = profile['base_util']
        
        # Apply temporal modulation
        target_util = target_util * week_factor
        
        # Add realistic noise - MATCH TRAINING VARIANCE!
        # Training σ ≈ 0.066, so use 100% of util_std (not 30%)
        noise = np.random.normal(0, profile['util_std'] * 1.0)  # ✅ Was 0.3 → 1.0
        target_util = np.clip(target_util + noise, 0.01, 0.98)
        
        # ================================
        # STEP 2: TRANSFORM BYTES_SENT
        # ================================
        # This is WHERE transform happens!
        # We take simulator's small bytes_sent and scale to realistic value
        
        # 2.1 Calculate target bytes (what dataset shows at this utilization)
        if target_util > 0.7:
            # High utilization = peak traffic
            target_bytes = profile['bytes_per_sec_peak'] * duration
        else:
            # Normal utilization
            # Interpolate between mean and peak based on utilization
            util_ratio = target_util / 0.7  # 0.7 = threshold for peak
            target_bytes = profile['bytes_per_sec_mean'] * duration
            target_bytes += (profile['bytes_per_sec_peak'] - profile['bytes_per_sec_mean']) * util_ratio * duration
        
        # 2.2 Blend simulator signal with target (optional)
        # If simulator has traffic, we can use it as a signal
        # But we ALWAYS scale to realistic range
        if sim_bytes > 0:
            # Simulator has traffic - use it as indicator but scale up
            blend_factor = 0.9  # 90% target, 10% simulator
            bytes_sent = target_bytes * blend_factor + sim_bytes * (1 - blend_factor)
            
            # But ensure we're still in realistic range
            bytes_sent = max(bytes_sent, target_bytes * 0.8)  # At least 80% of target
            bytes_sent = min(bytes_sent, target_bytes * 1.2)  # At most 120% of target
        else:
            # No simulator traffic - use pure target (realistic baseline)
            bytes_sent = target_bytes
        
        # Add small variance
        bytes_sent *= np.random.uniform(0.85, 1.15)
        
        # ================================
        # STEP 3: CALCULATE OTHER METRICS
        # ================================
        # Now we have realistic bytes_sent and utilization
        # Calculate all other metrics with proper correlations
        
        capacity_bps = link['capacity_bps']
        utilization = target_util  # Use our calculated realistic utilization
        bitrate_bps = utilization * capacity_bps
        
        # Loss rate (correlated with utilization)
        if utilization > 0.75:
            loss_rate = profile['loss_base'] + (utilization - 0.75) ** 2 * 0.8
        elif utilization > 0.6:
            loss_rate = profile['loss_base'] + (utilization - 0.6) * 0.05
        else:
            loss_rate = profile['loss_base'] + utilization * 0.003
        
        # Link-specific loss multipliers
        if 'space' in link_type.lower():
            loss_rate *= 1.5
        if 'sea' in link_type.lower():
            loss_rate *= 2.0
        
        loss_rate = np.clip(loss_rate, 0, 0.3)
        
        # Jitter (correlated with utilization and loss)
        jitter = profile['jitter_base'] + utilization * 50 + loss_rate * 200
        
        if utilization > 0.8:
            jitter += 40  # Queue buildup
        
        # Mobility jitter
        if 'air' in link_type.lower() or 'sea' in link_type.lower():
            jitter *= 1.4
        
        jitter = np.clip(jitter, 2, 200)
        
        # RTT (base latency + queueing delay + propagation variance)
        base_latency = link['base_latency_milliseconds']
        propagation_var = np.random.normal(0, 10) if 'space' in link_type.lower() else np.random.normal(0, 3)
        queue_delay = utilization * base_latency * 0.6
        
        rtt_milliseconds = base_latency + queue_delay + propagation_var
        rtt_milliseconds = np.clip(rtt_milliseconds, base_latency * 0.8, base_latency * 3.5)
        
        # Link latency (base with small variance)
        link_latency = base_latency * np.random.uniform(0.9, 1.2)
        
        # ================================
        # STEP 4: TEMPORAL FEATURES
        # ================================
        hour_sin = math.sin(2 * math.pi * hour / 24)
        hour_cos = math.cos(2 * math.pi * hour / 24)
        day_sin = math.sin(2 * math.pi * day_of_week / 7)
        day_cos = math.cos(2 * math.pi * day_of_week / 7)
        
        # ================================
        # STEP 5: DERIVED METRICS
        # ================================
        throughput_mbps = bitrate_bps / 1e6
        
        # Quality score (reliability-based)
        reliability = link.get('reliability_score', 0.95)
        quality_score = reliability * (1 - loss_rate) * (1 - min(jitter / 100, 0.5))
        quality_score = np.clip(quality_score, 0, 1)
        
        efficiency = utilization * quality_score
        
        # ================================
        # RETURN REALISTIC METRICS
        # ================================
        return {
            'timestamp': timestamp,
            'bytes_sent': round(bytes_sent, 1),
            'bitrate_bps': round(bitrate_bps, 6),
            'rtt_milliseconds': round(rtt_milliseconds, 4),
            'loss_rate': round(loss_rate, 10),
            'jitter_milliseconds': round(jitter, 6),
            'link_latency_milliseconds': round(link_latency, 6),
            'capacity_bps': capacity_bps,
            'source_layer': link['source_layer'],
            'destination_layer': link['destination_layer'],
            'link_id': link['link_id'],
            'hour': hour,
            'day_of_week': day_of_week,
            'is_weekend': 1 if is_weekend else 0,
            'hour_sin': round(hour_sin, 10),
            'hour_cos': round(hour_cos, 10),
            'day_sin': round(day_sin, 10),
            'day_cos': round(day_cos, 10),
            'utilization': round(utilization, 10),
            'throughput_mbps': round(throughput_mbps, 10),
            'quality_score': round(quality_score, 10),
            'efficiency': round(efficiency, 10),
        }
    
    def generate_metrics(self, link, content_length=None):
        """
        Legacy method - redirects to transform_traffic()
        
        This maintains backward compatibility with existing code.
        Internally converts to transform approach.
        
        Args:
            link: dict with link properties
            content_length: bytes of message (optional)
        
        Returns:
            dict with realistic metrics
        """
        # If we have content_length, treat it as raw traffic
        # Otherwise, use realistic baseline (0 bytes from simulator)
        raw_traffic = {
            'bytes_sent': content_length if content_length else 0,
            'duration': 1.0
        }
        
        # Use transform method (THE CORE)
        return self.transform_traffic(raw_traffic, link)


# ============================================
# DEMO - Transform Approach
# ============================================
def demo():
    """Test Transform approach with various simulator inputs"""
    print("=" * 70)
    print("🧪 Traffic Adapter Demo - TRANSFORM MODE")
    print("=" * 70)
    
    adapter = TrafficAdapter()
    
    # Test link (air → ground - high traffic link)
    link = {
        'link_id': 'LINK_AIR_GROUND_01',
        'source_layer': 'air',
        'destination_layer': 'ground',
        'capacity_bps': 60_000_000,  # 60 Mbps
        'base_latency_milliseconds': 50,
        'reliability_score': 0.9
    }
    
    print(f"\n📡 Test Link: {link['link_id']}")
    print(f"   Type: {link['source_layer']} → {link['destination_layer']}")
    print(f"   Capacity: {link['capacity_bps']/1e6:.1f} Mbps")
    
    # ================================
    # TEST 1: Transform SMALL traffic
    # ================================
    print(f"\n" + "=" * 70)
    print(f"🔬 TEST 1: Transform SMALL simulator traffic (10 KB)")
    print("=" * 70)
    
    raw_traffic_small = {
        'bytes_sent': 10_000,  # Only 10 KB from simulator
        'duration': 1.0
    }
    
    metrics = adapter.transform_traffic(raw_traffic_small, link)
    
    print(f"\n� INPUT (Simulator):")
    print(f"   bytes_sent:  {raw_traffic_small['bytes_sent']:>12,} bytes (~{raw_traffic_small['bytes_sent']/125:.1f} Kbps)")
    
    print(f"\n📤 OUTPUT (After Transform):")
    print(f"   bytes_sent:  {metrics['bytes_sent']:>12,.0f} bytes (~{metrics['bytes_sent']*8/1e6:.2f} Mbps)")
    print(f"   utilization: {metrics['utilization']:>12.2%}")
    print(f"   bitrate:     {metrics['bitrate_bps']/1e6:>12.2f} Mbps")
    print(f"   loss_rate:   {metrics['loss_rate']:>12.4%}")
    print(f"   jitter:      {metrics['jitter_milliseconds']:>12.2f} ms")
    print(f"   rtt:         {metrics['rtt_milliseconds']:>12.2f} ms")
    
    print(f"\n🎯 SCALE FACTOR: {metrics['bytes_sent'] / raw_traffic_small['bytes_sent']:.1f}x")
    print(f"   → Simulator sent {raw_traffic_small['bytes_sent']:,} bytes")
    print(f"   → Output shows {metrics['bytes_sent']:,.0f} bytes (realistic for this link/time)")
    
    # ================================
    # TEST 2: Transform ZERO traffic
    # ================================
    print(f"\n" + "=" * 70)
    print(f"🔬 TEST 2: Transform ZERO simulator traffic")
    print("=" * 70)
    
    raw_traffic_zero = {
        'bytes_sent': 0,  # No traffic from simulator
        'duration': 1.0
    }
    
    metrics_zero = adapter.transform_traffic(raw_traffic_zero, link)
    
    print(f"\n📥 INPUT (Simulator):")
    print(f"   bytes_sent:  {raw_traffic_zero['bytes_sent']:>12} bytes (ZERO traffic)")
    
    print(f"\n📤 OUTPUT (After Transform):")
    print(f"   bytes_sent:  {metrics_zero['bytes_sent']:>12,.0f} bytes (~{metrics_zero['bytes_sent']*8/1e6:.2f} Mbps)")
    print(f"   utilization: {metrics_zero['utilization']:>12.2%}")
    print(f"   bitrate:     {metrics_zero['bitrate_bps']/1e6:>12.2f} Mbps")
    
    print(f"\n💡 Even with ZERO simulator input, output is realistic!")
    print(f"   → Adapter generates baseline traffic matching dataset")
    print(f"   → ML model can still predict accurately")
    
    # ================================
    # TEST 3: Compare with legacy method
    # ================================
    print(f"\n" + "=" * 70)
    print(f"🔬 TEST 3: Compare transform vs legacy generate_metrics()")
    print("=" * 70)
    
    # Legacy method (redirects to transform internally)
    metrics_legacy = adapter.generate_metrics(link, content_length=52)
    
    print(f"\n📥 INPUT (Legacy method):")
    print(f"   content_length: 52 bytes")
    
    print(f"\n📤 OUTPUT:")
    print(f"   bytes_sent:  {metrics_legacy['bytes_sent']:>12,.0f} bytes")
    print(f"   utilization: {metrics_legacy['utilization']:>12.2%}")
    print(f"   bitrate:     {metrics_legacy['bitrate_bps']/1e6:>12.2f} Mbps")
    
    print(f"\n✅ Legacy method now uses transform internally")
    print(f"   → Backward compatible")
    print(f"   → Same realistic output")
    
    # ================================
    # TEST 4: Time series
    # ================================
    print(f"\n" + "=" * 70)
    print(f"🔬 TEST 4: Multiple samples (time series)")
    print("=" * 70)
    
    print(f"\n{'Sample':>6} {'Sim Bytes':>12} {'Output Bytes':>15} {'Util':>8} {'Bitrate (Mbps)':>15} {'Loss':>8}")
    print("-" * 70)
    
    for i in range(5):
        # Simulator sends varying traffic
        sim_bytes = np.random.randint(5000, 50000)
        raw = {'bytes_sent': sim_bytes, 'duration': 1.0}
        m = adapter.transform_traffic(raw, link)
        
        print(f"{i+1:>6} {sim_bytes:>12,} {m['bytes_sent']:>15,.0f} "
              f"{m['utilization']:>8.2%} {m['bitrate_bps']/1e6:>15.2f} "
              f"{m['loss_rate']:>8.4%}")
    
    print("\n✅ Demo complete!")
    print("\n" + "=" * 70)
    print("📊 KEY OBSERVATIONS:")
    print("=" * 70)
    print("1. Output bytes >> Input bytes (scaled to dataset)")
    print("2. Utilization realistic for current time/link type")
    print("3. Metrics properly correlated (loss ↔ util, jitter ↔ loss)")
    print("4. Even ZERO input produces realistic output")
    print("5. Ready for ML prediction!")
    print("=" * 70)


if __name__ == '__main__':
    demo()
