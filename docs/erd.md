# License Tracker - Entity Relationship Diagram

## Data Flow

```
User checks out license  ──►  license_details (ACTIVE / LIVE usage)
                                     │
User checks in license   ──►  record moves to license_history_logs (HISTORICAL)
                                     │
User denied a license    ──►  license_denials (links user + license info)
                                     │
Scheduler (every 5 min)  ──►  realtime_usage_snapshots (periodic snapshot of license_details)
```

```mermaid
erDiagram
    local_users {
        int id PK
        varchar login UK
        varchar email
        varchar password_hash
        enum type "ADMIN, USER"
        varchar site_code
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    license_details {
        int id PK
        int user_id FK
        varchar application
        varchar region
        varchar user
        varchar host
        varchar feature
        varchar user_key
        int license_used
        varchar site_code
        datetime check_out
        datetime check_in
        varchar spent_hours
        int total_license
        int total_license_used
        datetime created_at
    }

    license_history_logs {
        int id PK
        int user_id FK
        varchar application
        varchar region
        varchar user
        varchar server
        varchar host
        varchar software
        varchar feature
        varchar version
        varchar user_key
        datetime date_time
        datetime check_out
        datetime check_in
        varchar spent_hours
        int license_used
        varchar site_code
        int total_license
        int total_license_used
        datetime created_at
    }

    license_costs {
        int id PK
        varchar vendor
        varchar feature UK
        float cost_per_license
        varchar currency
        varchar billing_period
        text notes
        datetime created_at
        datetime updated_at
    }

    license_denials {
        int id PK
        int user_id FK
        varchar application
        varchar region
        varchar user
        varchar host
        varchar feature
        varchar reason
        datetime denied_at
        int total_license
        int total_license_used
        datetime created_at
    }

    realtime_usage_snapshots {
        int id PK
        varchar application
        varchar region
        varchar feature
        int total_license
        int used_license
        datetime snapshot_time
        datetime created_at
    }

    dashboard_layouts {
        int id PK
        int user_id FK
        varchar layout_name
        text layout_json
        boolean is_default
        datetime created_at
        datetime updated_at
    }

    app_settings {
        int id PK
        varchar setting_key UK
        text setting_value
        varchar setting_type
        varchar description
        datetime created_at
        datetime updated_at
    }

    local_users ||--o{ license_details : "checks out licenses"
    local_users ||--o{ license_denials : "denied checkout attempts"
    local_users ||--o{ dashboard_layouts : "has layouts"
    license_details ||--o{ license_history_logs : "moves to on check-in"
    license_details ||--o{ realtime_usage_snapshots : "periodic snapshots"
    license_details ||--o{ license_denials : "denial references license info"
    license_costs }o--o{ license_details : "cost per vendor+feature"
    license_costs }o--o{ license_history_logs : "cost per vendor+feature"
```

## Relationships

- **local_users → license_details**: Users check out licenses. `license_details` holds all currently **active/live** checkouts
- **license_details → license_history_logs**: When a user checks a license back in, the record **moves** from `license_details` to `license_history_logs` (completed usage)
- **local_users → license_denials**: When a user attempts to check out a license but is denied (e.g. no licenses available), a denial record is created linking the **user** and the **license info** (application, feature, etc.)
- **license_details → realtime_usage_snapshots**: The scheduler periodically snapshots the current state of `license_details` into `realtime_usage_snapshots`
- **local_users → dashboard_layouts**: One user can have multiple dashboard layouts (FK: `user_id`)
- **license_costs → license_details / license_history_logs**: Cost data maps to vendor+feature combinations
- **app_settings**: Standalone configuration table (LDAP, AI keys, etc.)

## Lifecycle

1. **Check-out**: User requests a license → new row in `license_details` (check_out = now, check_in = NULL)
2. **Active usage**: License is in use → visible in live/realtime views, captured by scheduler snapshots
3. **Check-in**: User releases the license → `license_details` row gets check_in timestamp, spent_hours calculated, then record is copied to `license_history_logs` and removed from `license_details`
4. **Denial**: If no licenses are available when user requests one → `license_denials` row created with user info + license info + reason
