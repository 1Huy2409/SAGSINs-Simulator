"""
Traffic Adapter for SAGSIN Simulator
=====================================
Generates realistic traffic metrics matching training dataset distribution

Purpose:
- Replace simple random generation with realistic patterns
- Match training data statistics (mean, std, correlations)
- Apply link-type specific characteristics (space_ground, air_ground, etc.)
- Output format matches exactly with training dataset

Author: PBL4 Team
Date: 2025-11-06
"""

import numpy as np
import math
from datetime import datetime


class TrafficAdapter:
    """
    Generate realistic traffic metrics matching training distribution
    
    Based on gendata.py patterns:
    - Link-specific characteristics (space_ground: stable, air_ground: bursty, etc.)
    - Hourly/daily cycles with peak hours
    - Weekend effects
    - Correlations: util ↔ loss, util ↔ jitter, util ↔ rtt
    """
    
    # ============================================
    # LINK TYPE PROFILES (từ gendata.py)
    # ============================================
    LINK_PROFILES = {
        'space_ground': {
            'base_util': 0.35,
            'util_variance': 0.05,
            'loss_base': 0.002,
            'jitter_base': 15,
            'peak_factor': 1.2,
            'weekend_factor': 0.85,
            'description': 'SATELLITE → GROUND: Stable, low util, high latency'
        },
        'space_air': {
            'base_util': 0.45,
            'util_variance': 0.12,
            'loss_base': 0.003,
            'jitter_base': 20,
            'peak_factor': 1.8,
            'weekend_factor': 1.0,
            'description': 'SATELLITE → UAV: Variable, mobility effects'
        },
        'air_ground': {
            'base_util': 0.65,
            'util_variance': 0.10,
            'loss_base': 0.001,
            'jitter_base': 8,
            'peak_factor': 2.2,
            'weekend_factor': 0.45,
            'description': 'UAV → GROUND: HIGH TRAFFIC, strong peaks'
        },
        'space_space': {
            'base_util': 0.30,
            'util_variance': 0.02,
            'loss_base': 0.0002,
            'jitter_base': 3,
            'peak_factor': 1.0,
            'weekend_factor': 1.0,
            'description': 'SATELLITE ↔ SATELLITE: Very stable, no peaks'
        },
        'ground_sea': {
            'base_util': 0.40,
            'util_variance': 0.15,
            'loss_base': 0.008,
            'jitter_base': 25,
            'peak_factor': 1.3,
            'weekend_factor': 1.0,
            'description': 'GROUND → SHIP: Variable, high weather impact'
        },
        'default': {
            'base_util': 0.45,
            'util_variance': 0.08,
            'loss_base': 0.002,
            'jitter_base': 10,
            'peak_factor': 1.0,
            'weekend_factor': 1.0,
            'description': 'Default profile for unknown link types'
        }
    }
    
    def __init__(self):
        """Initialize adapter"""
        print("✅ TrafficAdapter initialized with realistic SAGSIN patterns")
    
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
    
    def generate_metrics(self, link, content_length=None):
        """
        Generate realistic traffic metrics
        
        Args:
            link: dict with keys:
                - link_id
                - source_layer, destination_layer
                - capacity_bps
                - base_latency_milliseconds
                - reliability_score
            content_length: bytes sent (optional, for bytes_sent calculation)
        
        Returns:
            dict with all metrics matching training dataset format
        """
        # Current time
        now = datetime.utcnow()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        hour = now.hour
        day_of_week = now.weekday()
        is_weekend = day_of_week >= 5
        
        # Get link profile
        profile = self.get_link_profile(link['source_layer'], link['destination_layer'])
        
        # ================================
        # TEMPORAL PATTERNS
        # ================================
        
        # 1. Hourly pattern (business hours, peak hours)
        link_type = f"{link['source_layer']}_{link['destination_layer']}"
        
        if 'air_ground' in link_type.lower():
            # Strong business traffic peaks
            if 7 <= hour <= 9:
                hour_factor = 2.0  # Morning peak
            elif 12 <= hour <= 13:
                hour_factor = 1.3  # Lunch
            elif 17 <= hour <= 19:
                hour_factor = 2.2  # Evening peak
            elif 0 <= hour <= 6:
                hour_factor = 0.15  # Night
            else:
                hour_factor = 1.0
        elif 'space_air' in link_type.lower():
            # UAV daytime operation
            if 6 <= hour <= 20:
                hour_factor = profile['peak_factor']
            else:
                hour_factor = 0.1  # UAV returns to base
        elif link_type.lower() in ['space_ground', 'ground_sea']:
            # Moderate business hours
            if 8 <= hour <= 18:
                hour_factor = profile['peak_factor']
            else:
                hour_factor = 0.85
        else:
            hour_factor = 1.0
        
        # 2. Weekend factor
        week_factor = profile['weekend_factor'] if is_weekend else 1.0
        
        # 3. Random noise
        noise = np.random.normal(0, profile['util_variance'])
        
        # ================================
        # UTILIZATION
        # ================================
        utilization = profile['base_util'] * hour_factor * week_factor + noise
        utilization = np.clip(utilization, 0.01, 0.98)
        
        # ================================
        # BITRATE & BYTES
        # ================================
        capacity_bps = link['capacity_bps']
        bitrate_bps = utilization * capacity_bps
        
        # Bytes sent (5 seconds interval assumed)
        if content_length is not None:
            # Use provided content length with overhead
            bytes_sent = content_length * np.random.uniform(0.9, 1.1)
        else:
            # Estimate from bitrate (5s interval)
            interval_seconds = 5
            bytes_sent = bitrate_bps * interval_seconds / 8.0
        
        # ================================
        # LOSS RATE (correlated with util)
        # ================================
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
        
        # ================================
        # JITTER (correlated with util and loss)
        # ================================
        jitter = profile['jitter_base'] + utilization * 50 + loss_rate * 200
        
        if utilization > 0.8:
            jitter += 40  # Queue buildup
        
        # Mobility jitter
        if 'air' in link_type.lower() or 'sea' in link_type.lower():
            jitter *= 1.4
        
        jitter = np.clip(jitter, 2, 200)
        
        # ================================
        # RTT (base latency + queue delay + variance)
        # ================================
        base_latency = link['base_latency_milliseconds']
        propagation_var = np.random.normal(0, 10) if 'space' in link_type.lower() else np.random.normal(0, 3)
        queue_delay = utilization * base_latency * 0.6
        
        rtt_milliseconds = base_latency + queue_delay + propagation_var
        rtt_milliseconds = np.clip(rtt_milliseconds, base_latency * 0.8, base_latency * 3.5)
        
        # Link latency (base with small variance)
        link_latency = base_latency * np.random.uniform(0.9, 1.2)
        
        # ================================
        # TEMPORAL FEATURES (cyclic encoding)
        # ================================
        hour_sin = math.sin(2 * math.pi * hour / 24)
        hour_cos = math.cos(2 * math.pi * hour / 24)
        day_sin = math.sin(2 * math.pi * day_of_week / 7)
        day_cos = math.cos(2 * math.pi * day_of_week / 7)
        
        # ================================
        # DERIVED METRICS
        # ================================
        throughput_mbps = bitrate_bps / 1e6
        
        # Quality score (reliability-based)
        reliability = link.get('reliability_score', 0.95)
        quality_score = reliability * (1 - loss_rate) * (1 - min(jitter / 100, 0.5))
        quality_score = np.clip(quality_score, 0, 1)
        
        efficiency = utilization * quality_score
        
        # ================================
        # RETURN METRICS (exact format as training)
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


# ============================================
# DEMO
# ============================================
def demo():
    """Test adapter với link mẫu"""
    print("=" * 70)
    print("🧪 Traffic Adapter Demo")
    print("=" * 70)
    
    adapter = TrafficAdapter()
    
    # Test link (space → ground)
    link = {
        'link_id': 'LINK_SPACE_GROUND_01',
        'source_layer': 'space',
        'destination_layer': 'ground',
        'capacity_bps': 30_000_000,  # 30 Mbps
        'base_latency_milliseconds': 250,
        'reliability_score': 0.95
    }
    
    print(f"\n📡 Test Link: {link['link_id']}")
    print(f"   Type: {link['source_layer']} → {link['destination_layer']}")
    print(f"   Capacity: {link['capacity_bps']/1e6:.1f} Mbps")
    
    # Generate 5 samples
    print(f"\n📊 Generating 5 realistic samples:")
    print(f"{'Timestamp':<20} {'Util':>6} {'Bitrate (Mbps)':>15} {'Loss':>8} {'Jitter':>8} {'RTT':>8}")
    print("-" * 70)
    
    for _ in range(5):
        metrics = adapter.generate_metrics(link, content_length=1024)
        print(f"{metrics['timestamp']:<20} "
              f"{metrics['utilization']:>6.3f} "
              f"{metrics['throughput_mbps']:>15.2f} "
              f"{metrics['loss_rate']:>8.4f} "
              f"{metrics['jitter_milliseconds']:>8.1f} "
              f"{metrics['rtt_milliseconds']:>8.1f}")
    
    print("\n✅ Demo complete!")
    print("\nFeatures match training dataset:")
    print("   - Realistic utilization patterns (time-based)")
    print("   - Correlated loss/jitter/rtt")
    print("   - Link-type specific characteristics")


if __name__ == '__main__':
    demo()
