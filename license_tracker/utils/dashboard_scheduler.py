#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Scheduler jobs for dashboard: realtime usage snapshots and daily cleanup."""

import random
from datetime import datetime, timedelta
from license_tracker.logger import logger
from license_tracker.models import db


# Software configurations matching the system's actual license servers
APPS_CONFIG = {
    'MSC': {
        'features': [
            ('nastran', 100),
            ('patran', 50),
            ('marc', 40),
        ]
    },
    'Altair': {
        'features': [
            ('hyperworks', 75),
            ('hypermesh', 75),
            ('radioss', 60),
        ]
    },
    'RLM': {
        'features': [
            ('masta', 25),
        ]
    },
    'Particleworks': {
        'features': [
            ('particleworks', 10),
        ]
    }
}

REGIONS = ['EU', 'APAC', 'AME']

USERS = [
    ('john.doe', 'workstation-01'),
    ('jane.smith', 'workstation-02'),
    ('bob.wilson', 'workstation-03'),
    ('alice.chen', 'workstation-04'),
    ('mike.jones', 'workstation-10'),
    ('sarah.lee', 'workstation-11'),
    ('david.kim', 'workstation-12'),
    ('emma.white', 'workstation-13'),
    ('chris.brown', 'workstation-14'),
]

DENIAL_REASONS = [
    'All licenses in use',
    'License server unreachable',
    'Feature not available in license pool',
    'Maximum user limit reached',
]


def generate_realtime_snapshot():
    """Generate a realtime usage snapshot for all applications.
    Called every 5 minutes by the scheduler.
    Also randomly generates a few denials.
    """
    from license_tracker.models.realtime_usage_snapshot import RealtimeUsageSnapshot
    from license_tracker.models.license_denial import LicenseDenial

    now = datetime.utcnow()
    snapshots = []
    denials = []

    try:
        for app_name, app_config in APPS_CONFIG.items():
            for feature, total_lic in app_config['features']:
                for region in REGIONS:
                    # Simulate usage with some randomness but realistic patterns
                    # Higher usage during work hours (8-18), lower outside
                    hour = now.hour
                    if 8 <= hour <= 18:
                        base_usage = random.uniform(0.3, 0.8)
                    elif 6 <= hour <= 20:
                        base_usage = random.uniform(0.15, 0.5)
                    else:
                        base_usage = random.uniform(0.02, 0.2)

                    used = int(total_lic * base_usage)
                    used = max(0, min(used, total_lic))

                    snapshot = RealtimeUsageSnapshot(
                        application=app_name,
                        region=region,
                        feature=feature,
                        total_license=total_lic,
                        used_license=used,
                        snapshot_time=now
                    )
                    snapshots.append(snapshot)

                    # ~5% chance of generating a denial per feature per region
                    if random.random() < 0.05 and used >= total_lic * 0.8:
                        username, host = random.choice(USERS)
                        denial = LicenseDenial(
                            application=app_name,
                            region=region,
                            user=username,
                            host=host,
                            feature=feature,
                            reason=random.choice(DENIAL_REASONS),
                            denied_at=now,
                            total_license=total_lic,
                            total_license_used=used
                        )
                        denials.append(denial)

        db.session.bulk_save_objects(snapshots)
        if denials:
            db.session.bulk_save_objects(denials)
        db.session.commit()

        logger.info(f"[Scheduler] Generated {len(snapshots)} usage snapshots and {len(denials)} denials at {now}")
    except Exception as err:
        db.session.rollback()
        logger.error(f"[Scheduler] Error generating realtime snapshot: {err}")


MAX_SNAPSHOT_ROWS = 50000
MAX_DENIAL_ROWS = 50000
MAX_HISTORY_ROWS = 50000


def cleanup_old_data():
    """Daily cleanup: delete oldest rows when any table exceeds 50,000 records.
    - realtime_usage_snapshots: trim to 50k by removing oldest
    - license_denials: trim to 50k by removing oldest, also purge >90 days
    - license_history_logs: trim to 50k by removing oldest
    This prevents the database from growing unbounded.
    """
    from license_tracker.models.realtime_usage_snapshot import RealtimeUsageSnapshot
    from license_tracker.models.license_denial import LicenseDenial
    from license_tracker.models.license_history_logs import LicenseHistoryLog

    try:
        # --- Realtime usage snapshots ---
        total_snapshots = RealtimeUsageSnapshot.query.count()
        if total_snapshots > MAX_SNAPSHOT_ROWS:
            excess = total_snapshots - MAX_SNAPSHOT_ROWS
            oldest = RealtimeUsageSnapshot.query.order_by(
                RealtimeUsageSnapshot.snapshot_time.asc()
            ).limit(excess).all()
            for record in oldest:
                db.session.delete(record)
            logger.info(f"[Cleanup] Snapshots exceeded {MAX_SNAPSHOT_ROWS}: deleted {len(oldest)} oldest (was {total_snapshots})")
        else:
            logger.info(f"[Cleanup] Snapshots OK: {total_snapshots}/{MAX_SNAPSHOT_ROWS}")

        # --- License denials ---
        # First purge anything older than 90 days regardless of count
        cutoff = datetime.utcnow() - timedelta(days=90)
        old_denials = LicenseDenial.query.filter(
            LicenseDenial.denied_at < cutoff
        ).delete()
        if old_denials:
            logger.info(f"[Cleanup] Deleted {old_denials} denials older than 90 days")

        # Then trim to cap if still over
        total_denials = LicenseDenial.query.count()
        if total_denials > MAX_DENIAL_ROWS:
            excess = total_denials - MAX_DENIAL_ROWS
            oldest_denials = LicenseDenial.query.order_by(
                LicenseDenial.denied_at.asc()
            ).limit(excess).all()
            for record in oldest_denials:
                db.session.delete(record)
            logger.info(f"[Cleanup] Denials exceeded {MAX_DENIAL_ROWS}: deleted {len(oldest_denials)} oldest (was {total_denials})")
        else:
            logger.info(f"[Cleanup] Denials OK: {total_denials}/{MAX_DENIAL_ROWS}")

        # --- License history logs ---
        total_history = LicenseHistoryLog.query.count()
        if total_history > MAX_HISTORY_ROWS:
            excess = total_history - MAX_HISTORY_ROWS
            oldest_hist = LicenseHistoryLog.query.order_by(
                LicenseHistoryLog.date_time.asc()
            ).limit(excess).all()
            for record in oldest_hist:
                db.session.delete(record)
            logger.info(f"[Cleanup] History exceeded {MAX_HISTORY_ROWS}: deleted {len(oldest_hist)} oldest (was {total_history})")
        else:
            logger.info(f"[Cleanup] History OK: {total_history}/{MAX_HISTORY_ROWS}")

        db.session.commit()
        logger.info("[Cleanup] Daily cleanup completed successfully")
    except Exception as err:
        db.session.rollback()
        logger.error(f"[Cleanup] Error during daily cleanup: {err}")
